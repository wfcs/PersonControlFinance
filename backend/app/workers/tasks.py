"""Celery tasks para sync Open Finance e notificações."""

from __future__ import annotations

import asyncio
import logging
from uuid import UUID

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.tasks.sync_all_tenants", bind=True, max_retries=3)
def sync_all_tenants(self) -> None:  # type: ignore[override]
    """Dispara sync de Open Finance para todos os tenants com conexões ativas."""
    asyncio.run(_sync_all_tenants_async())


async def _sync_all_tenants_async() -> None:
    from sqlalchemy import distinct, select

    from app.db.session import AsyncSessionLocal
    from app.models.account import Account

    async with AsyncSessionLocal() as db:
        result = await db.scalars(
            select(distinct(Account.tenant_id)).where(
                Account.pluggy_item_id.isnot(None),
                Account.is_active.is_(True),
            )
        )
        tenant_ids = result.all()

    for tid in tenant_ids:
        sync_tenant.delay(str(tid))
        logger.info("Dispatched sync for tenant %s", tid)


@celery_app.task(name="app.workers.tasks.sync_tenant", bind=True, max_retries=3)
def sync_tenant(self, tenant_id: str) -> None:  # type: ignore[override]
    """Sincroniza contas e transações de um tenant via Pluggy."""
    try:
        asyncio.run(_sync_tenant_async(UUID(tenant_id)))
    except Exception as exc:
        logger.exception("Failed to sync tenant %s", tenant_id)
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


async def _sync_tenant_async(tenant_id: UUID) -> None:
    from sqlalchemy import distinct, select

    from app.db.session import AsyncSessionLocal
    from app.models.account import Account
    from app.services import pluggy_service

    async with AsyncSessionLocal() as db:
        result = await db.scalars(
            select(distinct(Account.pluggy_item_id)).where(
                Account.tenant_id == tenant_id,
                Account.pluggy_item_id.isnot(None),
                Account.is_active.is_(True),
            )
        )
        item_ids = result.all()

        for item_id in item_ids:
            try:
                await pluggy_service.sync_item_accounts(item_id, tenant_id, db)
                await pluggy_service.sync_item_transactions(item_id, tenant_id, db)
                logger.info("Synced item %s for tenant %s", item_id, tenant_id)
            except Exception:
                logger.exception("Failed to sync item %s for tenant %s", item_id, tenant_id)

        await db.commit()


@celery_app.task(name="app.workers.tasks.send_notification")
def send_notification(to_email: str, subject: str, html_body: str) -> None:
    """Envia e-mail transacional via SendGrid."""
    from app.services import email_service

    email_service.send_email(to_email, subject, html_body)


@celery_app.task(name="app.workers.tasks.send_welcome_email")
def send_welcome_email(to_email: str, full_name: str | None = None) -> None:
    """Envia e-mail de boas-vindas após registro."""
    from app.services import email_service

    email_service.send_welcome(to_email, full_name)


@celery_app.task(name="app.workers.tasks.send_plan_upgrade_email")
def send_plan_upgrade_email(
    to_email: str, full_name: str | None, plan: str
) -> None:
    """Envia e-mail de confirmação de upgrade."""
    from app.services import email_service

    email_service.send_plan_upgrade(to_email, full_name, plan)


@celery_app.task(name="app.workers.tasks.send_sync_error_email")
def send_sync_error_email(
    to_email: str, full_name: str | None, error_detail: str
) -> None:
    """Envia notificação de erro de sincronização."""
    from app.services import email_service

    email_service.send_sync_error(to_email, full_name, error_detail)
