"""Celery tasks for async processing of webhooks and sync operations."""

from __future__ import annotations

import asyncio
import json
import logging
from uuid import UUID

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Run an async coroutine from a sync Celery task."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create a new loop in a thread if needed
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, coro).result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


async def _process_pluggy_webhook_async(webhook_log_id: str) -> None:
    """Async implementation of webhook processing."""
    from app.db.session import async_session_factory
    from app.models.webhook_log import WebhookLog
    from app.services.account_service import sync_from_pluggy

    async with async_session_factory() as db:
        try:
            from sqlalchemy import select

            result = await db.execute(
                select(WebhookLog).where(WebhookLog.id == UUID(webhook_log_id))
            )
            webhook_log = result.scalar_one_or_none()
            if webhook_log is None:
                logger.error("Webhook log %s not found", webhook_log_id)
                return

            payload = json.loads(webhook_log.payload)
            event_type = webhook_log.event_type

            if event_type in ("ITEM_UPDATED", "item/updated"):
                item_id = payload.get("itemId") or payload.get("id")
                if item_id and webhook_log.tenant_id:
                    await sync_from_pluggy(item_id, str(webhook_log.tenant_id), db)

            elif event_type in ("ITEM_ERROR", "item/error"):
                logger.warning("Pluggy item error: %s", payload)

            # Update status
            webhook_log.status = "processed"
            await db.commit()

        except Exception:
            logger.exception("Failed to process webhook %s", webhook_log_id)
            if webhook_log:
                webhook_log.status = "failed"
                await db.commit()


@celery_app.task(name="process_pluggy_webhook", bind=True, max_retries=3)
def process_pluggy_webhook(self, webhook_log_id: str) -> None:
    """Process a Pluggy webhook event asynchronously.

    Reads the webhook log from DB, determines action based on event type,
    and updates the log status.
    """
    try:
        _run_async(_process_pluggy_webhook_async(webhook_log_id))
    except Exception as exc:
        logger.exception("Webhook processing failed, retrying...")
        raise self.retry(exc=exc, countdown=60)


async def _sync_account_transactions_async(item_id: str, tenant_id: str) -> None:
    """Async implementation of account transaction sync."""
    from app.db.session import async_session_factory
    from app.services.account_service import sync_from_pluggy

    async with async_session_factory() as db:
        await sync_from_pluggy(item_id, tenant_id, db)


@celery_app.task(name="sync_account_transactions", bind=True, max_retries=3)
def sync_account_transactions(self, item_id: str, tenant_id: str) -> None:
    """Sync account transactions from Pluggy via Celery."""
    try:
        _run_async(_sync_account_transactions_async(item_id, tenant_id))
    except Exception as exc:
        logger.exception("Account sync failed, retrying...")
        raise self.retry(exc=exc, countdown=60)
