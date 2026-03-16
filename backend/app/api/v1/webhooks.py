"""Endpoints de webhooks (Pluggy e Stripe)."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Request, Response, status
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.account import Account
from app.models.webhook_log import WebhookLog
from app.schemas.pluggy import PluggyWebhookPayload
from app.services import pluggy_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/pluggy", status_code=status.HTTP_200_OK)
async def pluggy_webhook(request: Request, background_tasks: BackgroundTasks) -> Response:
    """
    Recebe notificações do Pluggy.
    Retorna 200 imediatamente e processa em background.
    """
    body = await request.json()
    payload = _parse_pluggy_payload(body)
    logger.info("Pluggy webhook: event=%s item_id=%s", payload.event, payload.item_id)

    # Log para auditoria
    background_tasks.add_task(_log_webhook, "pluggy", payload.event, payload.event_id, body)

    if payload.event in ("item/created", "item/updated"):
        background_tasks.add_task(_handle_item_event, payload)
    elif payload.event == "transactions/created":
        background_tasks.add_task(_handle_transactions_created, payload)
    elif payload.event == "transactions/updated":
        background_tasks.add_task(_handle_transactions_updated, payload)
    elif payload.event in ("item/error", "item/login_error"):
        background_tasks.add_task(_handle_item_error, payload)

    return Response(status_code=200)


# ── Parsers ──────────────────────────────────────────────────────────────────


def _parse_pluggy_payload(body: dict) -> PluggyWebhookPayload:
    """Converte camelCase do Pluggy para snake_case."""
    return PluggyWebhookPayload(
        event=body.get("event", ""),
        event_id=body.get("eventId"),
        item_id=body.get("itemId"),
        account_id=body.get("accountId"),
        triggered_by=body.get("triggeredBy"),
        client_user_id=body.get("clientUserId"),
        transactions_count=body.get("transactionsCount"),
        created_transactions_link=body.get("createdTransactionsLink"),
        transaction_ids=body.get("transactionIds"),
    )


# ── Handlers ─────────────────────────────────────────────────────────────────


async def _log_webhook(
    source: str, event: str, event_id: str | None, payload: dict
) -> None:
    async with AsyncSessionLocal() as db:
        try:
            log = WebhookLog(source=source, event=event, event_id=event_id, payload=payload)
            db.add(log)
            await db.commit()
        except Exception:
            await db.rollback()
            logger.exception("Failed to log webhook")


async def _handle_item_event(payload: PluggyWebhookPayload) -> None:
    """Item criado/atualizado — sync contas + transações."""
    if not payload.item_id or not payload.client_user_id:
        return

    tenant_id = _extract_tenant_id(payload.client_user_id)
    if not tenant_id:
        return

    async with AsyncSessionLocal() as db:
        try:
            await pluggy_service.sync_item_accounts(payload.item_id, tenant_id, db)
            await pluggy_service.sync_item_transactions(payload.item_id, tenant_id, db)
            await db.commit()
        except Exception:
            await db.rollback()
            logger.exception("Failed to sync item %s", payload.item_id)


async def _handle_transactions_created(payload: PluggyWebhookPayload) -> None:
    """Novas transações — sync completo do item."""
    if not payload.item_id or not payload.client_user_id:
        return

    tenant_id = _extract_tenant_id(payload.client_user_id)
    if not tenant_id:
        return

    async with AsyncSessionLocal() as db:
        try:
            await pluggy_service.sync_item_transactions(payload.item_id, tenant_id, db)
            await db.commit()
        except Exception:
            await db.rollback()
            logger.exception("Failed to sync transactions for item %s", payload.item_id)


async def _handle_transactions_updated(payload: PluggyWebhookPayload) -> None:
    """Transações atualizadas — busca por IDs e atualiza."""
    if not payload.transaction_ids or not payload.client_user_id:
        return

    from decimal import Decimal

    from app.integrations.pluggy_client import pluggy_client
    from app.models.transaction import Transaction

    tenant_id = _extract_tenant_id(payload.client_user_id)
    if not tenant_id:
        return

    result = await pluggy_client.get_transactions_by_ids(payload.transaction_ids)

    async with AsyncSessionLocal() as db:
        try:
            for pt in result.get("results", []):
                tx = await db.scalar(
                    select(Transaction).where(
                        Transaction.external_id == pt["id"],
                        Transaction.tenant_id == tenant_id,
                    )
                )
                if tx:
                    tx.amount = Decimal(str(pt["amount"]))
                    tx.description = pt.get("description", tx.description)
            await db.commit()
        except Exception:
            await db.rollback()
            logger.exception("Failed to update transactions")


async def _handle_item_error(payload: PluggyWebhookPayload) -> None:
    logger.error("Pluggy item error: item_id=%s event=%s", payload.item_id, payload.event)


# ── Helpers ──────────────────────────────────────────────────────────────────


def _extract_tenant_id(client_user_id: str) -> UUID | None:
    """Extrai tenant_id do client_user_id (formato 'tenant_id:user_id')."""
    try:
        return UUID(client_user_id.split(":")[0])
    except (ValueError, IndexError):
        logger.error("Invalid client_user_id: %s", client_user_id)
        return None



# ── Stripe Webhooks ──────────────────────────────────────────────────────────


@router.post("/stripe", status_code=status.HTTP_200_OK)
async def stripe_webhook(request: Request, background_tasks: BackgroundTasks) -> Response:
    """
    Recebe webhooks do Stripe.
    Verifica assinatura e processa evento.
    """
    import stripe
    from app.core.config import settings

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return Response(status_code=400)

    background_tasks.add_task(
        _log_webhook, "stripe", event["type"], event["id"], event["data"]["object"]
    )

    if event["type"] == "checkout.session.completed":
        background_tasks.add_task(_handle_stripe_checkout, event["data"]["object"])
    elif event["type"] == "customer.subscription.updated":
        background_tasks.add_task(_handle_stripe_subscription_updated, event["data"]["object"])
    elif event["type"] == "customer.subscription.deleted":
        background_tasks.add_task(_handle_stripe_subscription_deleted, event["data"]["object"])

    return Response(status_code=200)


async def _handle_stripe_checkout(session: dict) -> None:
    from app.services import stripe_service
    async with AsyncSessionLocal() as db:
        try:
            await stripe_service.handle_checkout_completed(session, db)
            await db.commit()
        except Exception:
            await db.rollback()
            logger.exception("Failed to handle Stripe checkout")


async def _handle_stripe_subscription_updated(subscription: dict) -> None:
    from app.services import stripe_service
    async with AsyncSessionLocal() as db:
        try:
            await stripe_service.handle_subscription_updated(subscription, db)
            await db.commit()
        except Exception:
            await db.rollback()
            logger.exception("Failed to handle Stripe subscription update")


async def _handle_stripe_subscription_deleted(subscription: dict) -> None:
    from app.services import stripe_service
    async with AsyncSessionLocal() as db:
        try:
            await stripe_service.handle_subscription_deleted(subscription, db)
            await db.commit()
        except Exception:
            await db.rollback()
            logger.exception("Failed to handle Stripe subscription deletion")
