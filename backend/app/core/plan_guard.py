"""Plan enforcement guards for multi-tenant SaaS endpoints.

Provides FastAPI dependencies and utility functions to check whether the
current tenant's plan allows a given action or resource creation.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.core.plan_limits import PLAN_LIMITS, RESOURCE_LIMIT_KEYS, Plan
from app.models.tenant import Tenant
from app.models.user import User


def _get_plan_limits(plan_str: str) -> dict[str, Any]:
    """Return the limits dict for the given plan string.

    Falls back to FREE plan limits for unknown plan values.
    """
    try:
        plan = Plan(plan_str)
    except ValueError:
        plan = Plan.FREE
    return PLAN_LIMITS[plan]


def require_plan(*allowed_plans: Plan):
    """Return a FastAPI dependency that rejects requests unless the tenant's
    plan is in *allowed_plans*.

    Usage::

        @router.get("/ai-insights", dependencies=[Depends(require_plan(Plan.PREMIUM))])
        async def ai_insights(): ...
    """

    async def _guard(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> None:
        result = await db.execute(
            select(Tenant.plan).where(Tenant.id == current_user.tenant_id)
        )
        plan_str = result.scalar_one_or_none()
        if plan_str is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant not found",
            )

        try:
            current_plan = Plan(plan_str)
        except ValueError:
            current_plan = Plan.FREE

        if current_plan not in allowed_plans:
            allowed_names = ", ".join(p.value for p in allowed_plans)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"This feature requires one of the following plans: {allowed_names}. "
                    f"Your current plan is '{current_plan.value}'. "
                    "Please upgrade to access this feature."
                ),
            )

    return _guard


async def check_resource_limit(
    db: AsyncSession,
    tenant_id: UUID | str,
    resource: str,
    model: Any,
) -> None:
    """Check whether the tenant has reached the limit for *resource*.

    Parameters
    ----------
    db:
        Active database session.
    tenant_id:
        UUID (or string representation) of the tenant.
    resource:
        One of ``"accounts"``, ``"categories"``, ``"goals"``.
    model:
        The SQLAlchemy model class (e.g. ``Account``, ``Category``, ``Goal``)
        that has a ``tenant_id`` column.

    Raises
    ------
    HTTPException 403
        If the current count meets or exceeds the plan limit.
    """
    if isinstance(tenant_id, str):
        tenant_id = UUID(tenant_id)

    limit_key = RESOURCE_LIMIT_KEYS.get(resource)
    if limit_key is None:
        raise ValueError(f"Unknown resource type: {resource!r}")

    # Fetch tenant's plan
    result = await db.execute(
        select(Tenant.plan).where(Tenant.id == tenant_id)
    )
    plan_str = result.scalar_one_or_none()
    if plan_str is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant not found",
        )

    limits = _get_plan_limits(plan_str)
    max_allowed = limits[limit_key]

    # -1 means unlimited
    if max_allowed == -1:
        return

    # Count existing resources for this tenant
    count_result = await db.execute(
        select(func.count()).select_from(model).where(model.tenant_id == tenant_id)
    )
    current_count = count_result.scalar_one()

    if current_count >= max_allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Plan limit reached: your '{plan_str}' plan allows a maximum "
                f"of {max_allowed} {resource}. You currently have {current_count}. "
                "Please upgrade your plan to add more."
            ),
        )


def require_feature(feature: str):
    """Return a FastAPI dependency that checks if a boolean feature flag is
    enabled for the tenant's plan.

    Usage::

        @router.get("/export", dependencies=[Depends(require_feature("export_csv"))])
        async def export_csv(): ...
    """

    async def _guard(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> None:
        result = await db.execute(
            select(Tenant.plan).where(Tenant.id == current_user.tenant_id)
        )
        plan_str = result.scalar_one_or_none()
        if plan_str is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant not found",
            )

        limits = _get_plan_limits(plan_str)
        if not limits.get(feature, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"The feature '{feature}' is not available on your "
                    f"'{plan_str}' plan. Please upgrade to access this feature."
                ),
            )

    return _guard
