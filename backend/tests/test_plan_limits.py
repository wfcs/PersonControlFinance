from __future__ import annotations

import pytest

from app.core.plan_limits import get_plan_limits


@pytest.mark.asyncio
async def test_free_plan_limits() -> None:
    limits = get_plan_limits("free")
    assert limits.max_accounts == 2
    assert limits.max_connections == 1
    assert limits.max_transactions_month == 100
    assert "basic_dashboard" in limits.features
    assert "reports" not in limits.features


@pytest.mark.asyncio
async def test_pro_plan_limits() -> None:
    limits = get_plan_limits("pro")
    assert limits.max_accounts == 10
    assert limits.max_connections == 3
    assert "reports" in limits.features
    assert "export_csv" in limits.features
    assert "ai_assistant" not in limits.features


@pytest.mark.asyncio
async def test_premium_plan_has_all_features() -> None:
    limits = get_plan_limits("premium")
    assert limits.max_accounts == 999
    assert "ai_assistant" in limits.features
    assert "patrimony" in limits.features
    assert "projections" in limits.features
    assert "pj_support" in limits.features


@pytest.mark.asyncio
async def test_unknown_plan_defaults_to_free() -> None:
    limits = get_plan_limits("nonexistent")
    assert limits.name == "free"
    assert limits.max_accounts == 2
