"""Webhook endpoints for receiving external notifications (Pluggy, etc.)."""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from fastapi import Depends

from app.models.webhook_log import WebhookLog

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/pluggy", status_code=status.HTTP_200_OK)
async def pluggy_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Receive Pluggy webhook notifications.

    Logs the event and dispatches a Celery task for async processing.
    Returns 200 immediately.
    """
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    event_type = payload.get("event", "UNKNOWN")
    # Pluggy webhooks may include itemId which maps to a tenant connection
    # For now, tenant_id is nullable on webhook_logs

    webhook_log = WebhookLog(
        source="pluggy",
        event_type=event_type,
        payload=json.dumps(payload),
        status="received",
        tenant_id=None,  # Will be resolved during async processing
    )
    db.add(webhook_log)
    await db.commit()
    await db.refresh(webhook_log)

    # Dispatch Celery task for async processing
    try:
        from app.workers.tasks import process_pluggy_webhook

        process_pluggy_webhook.delay(str(webhook_log.id))
    except Exception:
        # If Celery is not available (e.g., in tests), log and continue
        logger.warning("Could not dispatch Celery task for webhook %s", webhook_log.id)

    return {"detail": "Webhook received", "webhook_log_id": str(webhook_log.id)}
