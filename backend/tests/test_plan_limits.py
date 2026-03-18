"""Tests for plan limits system (unit tests)."""

import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.plan_limits import PLAN_LIMITS, RESOURCE_LIMIT_KEYS, Plan
from app.core.plan_guard import _get_plan_limits, check_resource_limit
from app.models.account import Account
from app.models.category import Category
from app.models.goal import Goal
from app.models.tenant import Tenant


# ── Plan enum and limits dict ─────────────────────────────────


class TestPlanLimits:
    def test_plan_enum_values(self):
        assert Plan.FREE.value == "free"
        assert Plan.PRO.value == "pro"
        assert Plan.PREMIUM.value == "premium"

    def test_all_plans_have_limits(self):
        for plan in Plan:
            assert plan in PLAN_LIMITS, f"Missing limits for plan: {plan}"

    def test_free_plan_limits(self):
        limits = PLAN_LIMITS[Plan.FREE]
        assert limits["max_accounts"] == 2
        assert limits["max_categories"] == 10
        assert limits["max_goals"] == 3
        assert limits["open_finance"] is False
        assert limits["ai_assistant"] is False
        assert limits["export_csv"] is False

    def test_pro_plan_limits(self):
        limits = PLAN_LIMITS[Plan.PRO]
        assert limits["max_accounts"] == 10
        assert limits["max_categories"] == 50
        assert limits["max_goals"] == 20
        assert limits["open_finance"] is True
        assert limits["ai_assistant"] is False
        assert limits["export_csv"] is True

    def test_premium_plan_unlimited(self):
        limits = PLAN_LIMITS[Plan.PREMIUM]
        assert limits["max_accounts"] == -1
        assert limits["max_categories"] == -1
        assert limits["max_goals"] == -1
        assert limits["open_finance"] is True
        assert limits["ai_assistant"] is True
        assert limits["export_csv"] is True

    def test_resource_limit_keys_mapping(self):
        assert RESOURCE_LIMIT_KEYS["accounts"] == "max_accounts"
        assert RESOURCE_LIMIT_KEYS["categories"] == "max_categories"
        assert RESOURCE_LIMIT_KEYS["goals"] == "max_goals"

    def test_get_plan_limits_known_plan(self):
        limits = _get_plan_limits("pro")
        assert limits["max_accounts"] == 10

    def test_get_plan_limits_unknown_falls_to_free(self):
        limits = _get_plan_limits("enterprise")
        assert limits == PLAN_LIMITS[Plan.FREE]

    def test_plan_hierarchy_limits_increase(self):
        """Verify that limits increase across plan tiers."""
        for key in ("max_accounts", "max_categories", "max_goals"):
            free_val = PLAN_LIMITS[Plan.FREE][key]
            pro_val = PLAN_LIMITS[Plan.PRO][key]
            premium_val = PLAN_LIMITS[Plan.PREMIUM][key]
            assert pro_val > free_val, f"PRO {key} should exceed FREE"
            # Premium is unlimited (-1), which conceptually exceeds PRO
            assert premium_val == -1 or premium_val > pro_val


# ── check_resource_limit integration ─────────────────────────


@pytest.fixture
async def db_session():
    """Get a test DB session from the override."""
    # Import here to use the test-configured session
    from tests.conftest import TestSessionLocal

    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
async def free_tenant(db_session: AsyncSession) -> Tenant:
    """Create a tenant on the free plan."""
    tenant = Tenant(
        name="Free Corp",
        slug=f"free-corp-{uuid.uuid4().hex[:6]}",
        plan="free",
    )
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    return tenant


@pytest.fixture
async def premium_tenant(db_session: AsyncSession) -> Tenant:
    """Create a tenant on the premium plan."""
    tenant = Tenant(
        name="Premium Corp",
        slug=f"premium-corp-{uuid.uuid4().hex[:6]}",
        plan="premium",
    )
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    return tenant


@pytest.mark.asyncio
async def test_check_resource_limit_under_limit(
    db_session: AsyncSession, free_tenant: Tenant
):
    """Should pass when under the limit."""
    # Free plan allows 2 accounts; we have 0
    await check_resource_limit(db_session, free_tenant.id, "accounts", Account)
    # No exception raised


@pytest.mark.asyncio
async def test_check_resource_limit_at_limit_raises(
    db_session: AsyncSession, free_tenant: Tenant
):
    """Should raise 403 when at the limit."""
    from fastapi import HTTPException

    # Add 2 accounts (free plan max)
    for i in range(2):
        db_session.add(
            Account(
                name=f"Account {i}",
                type="checking",
                tenant_id=free_tenant.id,
            )
        )
    await db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        await check_resource_limit(db_session, free_tenant.id, "accounts", Account)
    assert exc_info.value.status_code == 403
    assert "Plan limit reached" in exc_info.value.detail


@pytest.mark.asyncio
async def test_check_resource_limit_premium_unlimited(
    db_session: AsyncSession, premium_tenant: Tenant
):
    """Premium plan should allow unlimited resources."""
    # Add many accounts
    for i in range(50):
        db_session.add(
            Account(
                name=f"Account {i}",
                type="checking",
                tenant_id=premium_tenant.id,
            )
        )
    await db_session.commit()

    # Should not raise
    await check_resource_limit(db_session, premium_tenant.id, "accounts", Account)


@pytest.mark.asyncio
async def test_check_resource_limit_categories(
    db_session: AsyncSession, free_tenant: Tenant
):
    """Should enforce category limits on free plan."""
    from fastapi import HTTPException

    # Free plan allows 10 categories
    for i in range(10):
        db_session.add(
            Category(
                name=f"Category {i}",
                type="expense",
                tenant_id=free_tenant.id,
            )
        )
    await db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        await check_resource_limit(db_session, free_tenant.id, "categories", Category)
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_check_resource_limit_goals(
    db_session: AsyncSession, free_tenant: Tenant
):
    """Should enforce goal limits on free plan."""
    from decimal import Decimal

    from fastapi import HTTPException

    # Free plan allows 3 goals
    for i in range(3):
        db_session.add(
            Goal(
                name=f"Goal {i}",
                target_amount=Decimal("1000.00"),
                tenant_id=free_tenant.id,
            )
        )
    await db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        await check_resource_limit(db_session, free_tenant.id, "goals", Goal)
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_check_resource_limit_unknown_resource(
    db_session: AsyncSession, free_tenant: Tenant
):
    """Should raise ValueError for unknown resource types."""
    with pytest.raises(ValueError, match="Unknown resource type"):
        await check_resource_limit(db_session, free_tenant.id, "widgets", Account)


@pytest.mark.asyncio
async def test_check_resource_limit_string_tenant_id(
    db_session: AsyncSession, free_tenant: Tenant
):
    """Should accept tenant_id as a string."""
    # Should not raise (under limit)
    await check_resource_limit(
        db_session, str(free_tenant.id), "accounts", Account
    )
