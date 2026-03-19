from __future__ import annotations

import logging

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
        # TODO: Trigger account sync when Open Finance integration is ready

    elif event_type == "transaction/created":
        logger.info("New transactions for tenant %s", tenant_id)
        # TODO: Process new transactions

    return {"status": "processed", "tenant_id": tenant_id, "event": event_type}


@celery.task(name="send_notification")
def send_notification(user_email: str, subject: str, body: str) -> dict:
    """Send email notification (placeholder for SendGrid integration)."""
    logger.info("Sending notification to %s: %s", user_email, subject)
    return {"status": "sent", "to": user_email}
