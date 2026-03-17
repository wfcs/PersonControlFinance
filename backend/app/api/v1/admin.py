"""Endpoints do painel administrativo.

Apenas super-admins (configurados via ADMIN_EMAILS) podem acessar.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import AuthUser, DBSession, CurrentUser, get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])

# Lista de e-mails com acesso admin (configurável via env)
ADMIN_EMAILS: set[str] = set()


def _load_admin_emails() -> set[str]:
    global ADMIN_EMAILS
    if not ADMIN_EMAILS:
        from app.core.config import settings

        raw = getattr(settings, "ADMIN_EMAILS", "")
        if raw:
            ADMIN_EMAILS = {e.strip().lower() for e in raw.split(",") if e.strip()}
    return ADMIN_EMAILS


async def require_admin(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Dependency que exige acesso de admin."""
    admins = _load_admin_emails()
    if current_user.email.lower() not in admins:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores",
        )
    return current_user


AdminUser = CurrentUser  # alias para clareza


# ── Schemas ──────────────────────────────────────────────────────────────────


class TenantSummary(BaseModel):
    id: UUID
    name: str
    plan: str
    subscription_status: str
    user_count: int
    account_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class UserSummary(BaseModel):
    id: UUID
    email: str
    full_name: str | None
    is_active: bool
    is_verified: bool
    tenant_id: UUID
    tenant_name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminStats(BaseModel):
    total_tenants: int
    total_users: int
    total_accounts: int
    total_transactions: int
    tenants_by_plan: dict[str, int]
    active_users: int
    verified_users: int


class TenantUpdate(BaseModel):
    plan: str | None = None
    subscription_status: str | None = None


class UserUpdate(BaseModel):
    is_active: bool | None = None
    is_verified: bool | None = None


# ── Endpoints ────────────────────────────────────────────────────────────────


@router.get("/stats", response_model=AdminStats)
async def get_stats(
    db: DBSession,
    _admin: AdminUser = Depends(require_admin),
) -> AdminStats:
    """Estatísticas globais da plataforma."""
    from app.models.tenant import Tenant
    from app.models.user import User
    from app.models.account import Account
    from app.models.transaction import Transaction

    total_tenants = await db.scalar(select(func.count(Tenant.id))) or 0
    total_users = await db.scalar(select(func.count(User.id))) or 0
    total_accounts = await db.scalar(select(func.count(Account.id))) or 0
    total_transactions = await db.scalar(select(func.count(Transaction.id))) or 0
    active_users = await db.scalar(
        select(func.count(User.id)).where(User.is_active.is_(True))
    ) or 0
    verified_users = await db.scalar(
        select(func.count(User.id)).where(User.is_verified.is_(True))
    ) or 0

    # Tenants por plano
    plan_rows = await db.execute(
        select(Tenant.plan, func.count(Tenant.id)).group_by(Tenant.plan)
    )
    tenants_by_plan = {row[0]: row[1] for row in plan_rows}

    return AdminStats(
        total_tenants=total_tenants,
        total_users=total_users,
        total_accounts=total_accounts,
        total_transactions=total_transactions,
        tenants_by_plan=tenants_by_plan,
        active_users=active_users,
        verified_users=verified_users,
    )


@router.get("/tenants", response_model=list[TenantSummary])
async def list_tenants(
    db: DBSession,
    _admin: AdminUser = Depends(require_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    plan: str | None = None,
) -> list[TenantSummary]:
    """Lista todos os tenants da plataforma."""
    from app.models.tenant import Tenant
    from app.models.user import User
    from app.models.account import Account

    query = (
        select(
            Tenant,
            func.count(func.distinct(User.id)).label("user_count"),
            func.count(func.distinct(Account.id)).label("account_count"),
        )
        .outerjoin(User, User.tenant_id == Tenant.id)
        .outerjoin(Account, Account.tenant_id == Tenant.id)
        .group_by(Tenant.id)
        .order_by(Tenant.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    if plan:
        query = query.where(Tenant.plan == plan)

    result = await db.execute(query)
    rows = result.all()

    return [
        TenantSummary(
            id=tenant.id,
            name=tenant.name,
            plan=tenant.plan,
            subscription_status=tenant.subscription_status,
            user_count=user_count,
            account_count=account_count,
            created_at=tenant.created_at,
        )
        for tenant, user_count, account_count in rows
    ]


@router.patch("/tenants/{tenant_id}", response_model=TenantSummary)
async def update_tenant(
    tenant_id: UUID,
    data: TenantUpdate,
    db: DBSession,
    _admin: AdminUser = Depends(require_admin),
) -> TenantSummary:
    """Atualiza plano ou status de um tenant."""
    from app.models.tenant import Tenant
    from app.models.user import User
    from app.models.account import Account

    tenant = await db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")

    if data.plan is not None:
        tenant.plan = data.plan
    if data.subscription_status is not None:
        tenant.subscription_status = data.subscription_status

    await db.flush()

    # Conta users e accounts
    user_count = await db.scalar(
        select(func.count(User.id)).where(User.tenant_id == tenant_id)
    ) or 0
    account_count = await db.scalar(
        select(func.count(Account.id)).where(Account.tenant_id == tenant_id)
    ) or 0

    return TenantSummary(
        id=tenant.id,
        name=tenant.name,
        plan=tenant.plan,
        subscription_status=tenant.subscription_status,
        user_count=user_count,
        account_count=account_count,
        created_at=tenant.created_at,
    )


@router.get("/users", response_model=list[UserSummary])
async def list_users(
    db: DBSession,
    _admin: AdminUser = Depends(require_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    is_active: bool | None = None,
) -> list[UserSummary]:
    """Lista todos os usuários da plataforma."""
    from app.models.user import User
    from app.models.tenant import Tenant

    query = (
        select(User, Tenant.name.label("tenant_name"))
        .join(Tenant, Tenant.id == User.tenant_id)
        .order_by(User.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    if is_active is not None:
        query = query.where(User.is_active == is_active)

    result = await db.execute(query)
    rows = result.all()

    return [
        UserSummary(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            tenant_id=user.tenant_id,
            tenant_name=tenant_name,
            created_at=user.created_at,
        )
        for user, tenant_name in rows
    ]


@router.patch("/users/{user_id}", response_model=UserSummary)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    db: DBSession,
    _admin: AdminUser = Depends(require_admin),
) -> UserSummary:
    """Ativa/desativa ou verifica um usuário."""
    from app.models.user import User
    from app.models.tenant import Tenant

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if data.is_active is not None:
        user.is_active = data.is_active
    if data.is_verified is not None:
        user.is_verified = data.is_verified

    await db.flush()

    tenant = await db.get(Tenant, user.tenant_id)

    return UserSummary(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        tenant_id=user.tenant_id,
        tenant_name=tenant.name if tenant else "",
        created_at=user.created_at,
    )


@router.get("/webhook-logs")
async def list_webhook_logs(
    db: DBSession,
    _admin: AdminUser = Depends(require_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    source: str | None = None,
) -> list[dict]:
    """Lista logs de webhooks recebidos."""
    from app.models.webhook_log import WebhookLog

    query = (
        select(WebhookLog)
        .order_by(WebhookLog.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    if source:
        query = query.where(WebhookLog.source == source)

    result = await db.scalars(query)
    logs = result.all()

    return [
        {
            "id": str(log.id),
            "source": log.source,
            "event": log.event,
            "status": log.status,
            "payload": log.payload,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]
