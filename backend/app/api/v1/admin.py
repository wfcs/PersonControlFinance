from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_current_user
from app.db.session import get_session
from app.models.tenant import Tenant
from app.models.transaction import Transaction
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["Admin"])


def _require_admin(user: User) -> User:
    """Check if user email is in ADMIN_EMAILS list."""
    admin_emails = getattr(settings, "ADMIN_EMAILS", "")
    if isinstance(admin_emails, str):
        allowed = [e.strip() for e in admin_emails.split(",") if e.strip()]
    else:
        allowed = list(admin_emails)

    if user.email not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


@router.get("/stats")
async def platform_stats(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Platform-wide statistics (admin only)."""
    _require_admin(current_user)

    tenant_count = (await session.execute(select(func.count()).select_from(Tenant))).scalar()
    user_count = (await session.execute(select(func.count()).select_from(User))).scalar()
    txn_count = (await session.execute(select(func.count()).select_from(Transaction))).scalar()

    # Plan distribution
    plan_dist = await session.execute(
        select(Tenant.plan, func.count()).group_by(Tenant.plan)
    )
    plans = {row[0]: row[1] for row in plan_dist.all()}

    return {
        "total_tenants": tenant_count,
        "total_users": user_count,
        "total_transactions": txn_count,
        "plan_distribution": plans,
    }


@router.get("/tenants")
async def list_tenants(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """List all tenants (admin only)."""
    _require_admin(current_user)

    result = await session.execute(
        select(Tenant).order_by(Tenant.created_at.desc())
    )
    tenants = result.scalars().all()

    return [
        {
            "id": str(t.id),
            "name": t.name,
            "slug": t.slug,
            "plan": t.plan,
            "subscription_status": t.subscription_status,
            "user_count": len(t.users) if t.users else 0,
            "created_at": t.created_at.isoformat(),
        }
        for t in tenants
    ]
