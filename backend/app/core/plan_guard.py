"""Dependency factory para enforcement de limites por plano."""

from __future__ import annotations

from typing import Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import AuthUser, DBSession
from app.core.plan_limits import PLAN_LIMITS
from app.models.tenant import Tenant


def require_feature(feature: str) -> Callable:
    """
    Retorna uma dependência FastAPI que bloqueia acesso se o plano
    do tenant não inclui a feature solicitada.

    Uso:
        @router.get("/...", dependencies=[Depends(require_feature("open_finance"))])
    """

    async def _guard(
        current_user: AuthUser,
        db: DBSession,
    ) -> None:
        tenant = await db.get(Tenant, current_user.tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant não encontrado",
            )

        limits = PLAN_LIMITS.get(tenant.plan, PLAN_LIMITS["free"])
        if not limits.get(feature):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Feature '{feature}' requer upgrade de plano. Plano atual: {tenant.plan}",
            )

    return _guard


def require_account_limit() -> Callable:
    """Verifica se o tenant pode adicionar mais contas."""

    async def _guard(
        current_user: AuthUser,
        db: DBSession,
    ) -> None:
        from app.models.account import Account

        tenant = await db.get(Tenant, current_user.tenant_id)
        if not tenant:
            raise HTTPException(status_code=403, detail="Tenant não encontrado")

        limits = PLAN_LIMITS.get(tenant.plan, PLAN_LIMITS["free"])
        max_accounts = limits.get("max_accounts", 2)
        if max_accounts == -1:
            return  # ilimitado

        count = await db.scalar(
            select(Account.id)
            .where(Account.tenant_id == current_user.tenant_id, Account.is_active.is_(True))
            .with_only_columns(Account.id)
            .limit(max_accounts + 1)
        )
        # Simplificação: contar no service é melhor, mas aqui basta verificar
        from sqlalchemy import func
        total = await db.scalar(
            select(func.count()).select_from(Account).where(
                Account.tenant_id == current_user.tenant_id,
                Account.is_active.is_(True),
            )
        ) or 0

        if total >= max_accounts:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Limite de {max_accounts} contas atingido. Faça upgrade do plano.",
            )

    return _guard
