from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.plan_limits import get_plan_limits
from app.models.account import Account
from app.models.tenant import Tenant


def require_plan(required_features: list[str]):
    """FastAPI dependency factory: raises 403 if tenant plan lacks any required feature."""

    async def _guard(
        tenant_id: UUID,
        session: AsyncSession,
    ) -> None:
        result = await session.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = result.scalar_one_or_none()
        if tenant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found",
            )

        limits = get_plan_limits(tenant.plan)
        missing = [f for f in required_features if f not in limits.features]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Your plan ({tenant.plan}) does not include: {', '.join(missing)}. Upgrade to access this feature.",
            )

    return _guard


async def check_account_limit(
    tenant_id: UUID,
    session: AsyncSession,
) -> None:
    """Raises 403 if tenant has reached their max_accounts limit."""
    result = await session.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    limits = get_plan_limits(tenant.plan)

    count_result = await session.execute(
        select(func.count()).select_from(Account).where(Account.tenant_id == tenant_id)
    )
    current_count = count_result.scalar() or 0

    if current_count >= limits.max_accounts:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account limit reached ({limits.max_accounts} for {tenant.plan} plan). Upgrade your plan to add more accounts.",
        )
