from __future__ import annotations

import asyncio
import logging
import os

from app.workers.celery_app import celery

logger = logging.getLogger(__name__)


@celery.task(name="process_webhook")
def process_webhook(tenant_id: str, event_type: str, payload: dict) -> dict:
    """Process incoming webhook events asynchronously."""
    logger.info(
        "Processing webhook: tenant=%s event=%s",
        tenant_id,
        event_type,
    )

    if event_type == "item/updated":
        logger.info("Item updated for tenant %s — triggering account sync", tenant_id)

    elif event_type == "transaction/created":
        logger.info("New transactions for tenant %s", tenant_id)

    return {"status": "processed", "tenant_id": tenant_id, "event": event_type}


@celery.task(name="send_notification")
def send_notification(user_email: str, subject: str, body: str) -> dict:
    """Send email notification (placeholder for SendGrid integration)."""
    logger.info("Sending notification to %s: %s", user_email, subject)
    return {"status": "sent", "to": user_email}


@celery.task(name="process_recurrences")
def process_recurrences_task() -> dict:
    """Celery task to process all due recurrences across all tenants."""
    if os.environ.get("TESTING") == "1":
        return {"status": "skipped", "reason": "testing"}

    from uuid import UUID

    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    from app.core.config import settings
    from app.models.tenant import Tenant
    from app.services.recurrence_service import process_due_recurrences

    async def _run() -> dict:
        engine = create_async_engine(settings.DATABASE_URL)
        session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        total_created = 0
        async with session_factory() as session:
            result = await session.execute(select(Tenant.id))
            tenant_ids = [row[0] for row in result.all()]

            for tid in tenant_ids:
                txns = await process_due_recurrences(UUID(str(tid)), session)
                total_created += len(txns)

            await session.commit()
        await engine.dispose()
        return {"status": "completed", "transactions_created": total_created, "tenants_processed": len(tenant_ids)}

    return asyncio.run(_run())


@celery.task(name="sync_open_finance")
def sync_open_finance_task() -> dict:
    """Periodic sync with Open Finance provider (Pluggy).

    Placeholder — will be implemented when Pluggy integration is ready.
    Scans all accounts with pluggy_item_id and refreshes balances/transactions.
    """
    if os.environ.get("TESTING") == "1":
        return {"status": "skipped", "reason": "testing"}

    logger.info("Starting Open Finance sync job...")
    # TODO: Iterate tenants with pluggy_item_id, call Pluggy API, update balances
    return {"status": "completed", "synced_items": 0}


# Celery Beat schedule (configure in celery_app or settings)
celery.conf.beat_schedule = {
    "process-recurrences-daily": {
        "task": "process_recurrences",
        "schedule": 86400.0,  # every 24 hours
    },
    "sync-open-finance-hourly": {
        "task": "sync_open_finance",
        "schedule": 3600.0,  # every hour
    },
}
