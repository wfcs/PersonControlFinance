from __future__ import annotations

import logging
import os

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings
from app.db.session import get_session
from app.models.webhook_log import WebhookLog

# Inherit from main app's limiter or create a local one with same config
storage_uri = settings.REDIS_URL
if storage_uri.startswith("memory://") or settings.ENVIRONMENT == "development":
    storage_uri = "memory://"

limiter = Limiter(key_func=get_remote_address, storage_uri=storage_uri)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])
logger = logging.getLogger(__name__)


@router.post("/pluggy")
@limiter.limit(settings.RATE_LIMIT_WEBHOOKS)
async def pluggy_webhook(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Receive Pluggy webhook events for Open Finance sync updates."""
    payload = await request.json()
    event_type = payload.get("event", "unknown")
    tenant_id = payload.get("tenant_id")

    logger.info("Received Pluggy webhook: event=%s", event_type)

    # Log webhook
    if tenant_id:
        log = WebhookLog(
            source="pluggy",
            event_type=event_type,
            payload=payload,
            status="received",
            tenant_id=tenant_id,
        )
        session.add(log)
        await session.flush()

    # Dispatch to Celery for async processing
    if os.environ.get("TESTING") != "1" and tenant_id:
        try:
            from app.workers.tasks import process_webhook

            process_webhook.delay(str(tenant_id), event_type, payload)
        except Exception:
            logger.debug("Celery unavailable, skipping webhook processing")

    return {"status": "received", "event": event_type}
