"""Tests for the categorization engine."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.tenant import Tenant
from app.services.categorization_service import auto_categorize, KEYWORD_RULES


@pytest.fixture
async def db_session():
    """Get a test DB session from the override."""
    from tests.conftest import TestSessionLocal

    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
async def tenant_with_categories(db_session: AsyncSession) -> Tenant:
    """Create a tenant with some standard categories."""
    tenant = Tenant(
        name="Cat Test Corp",
        slug=f"cat-test-{uuid.uuid4().hex[:6]}",
        plan="free",
    )
    db_session.add(tenant)
    await db_session.flush()

    # Create categories matching our keyword rules
    for name in ["Transporte", "Alimentacao", "Entretenimento"]:
        db_session.add(
            Category(
                name=name,
                type="expense",
                tenant_id=tenant.id,
            )
        )
    await db_session.commit()
    await db_session.refresh(tenant)
    return tenant


@pytest.mark.asyncio
async def test_keyword_matching(db_session: AsyncSession, tenant_with_categories: Tenant):
    """Should match keywords in description to categories."""
    # "uber" should match "Transporte"
    result = await auto_categorize(
        "Uber Trip Downtown", str(tenant_with_categories.id), db_session
    )
    assert result is not None

    # "ifood" should match "Alimentacao"
    result = await auto_categorize(
        "iFood Delivery Order", str(tenant_with_categories.id), db_session
    )
    assert result is not None

    # "netflix" should match "Entretenimento"
    result = await auto_categorize(
        "Netflix Monthly Subscription", str(tenant_with_categories.id), db_session
    )
    assert result is not None


@pytest.mark.asyncio
async def test_auto_categorize_no_match(db_session: AsyncSession, tenant_with_categories: Tenant):
    """Should return None when no keyword matches."""
    result = await auto_categorize(
        "Random unknown transaction XYZ", str(tenant_with_categories.id), db_session
    )
    assert result is None
