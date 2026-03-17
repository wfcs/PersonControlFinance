"""Serviço de billing com Stripe."""

from __future__ import annotations

from uuid import UUID

import stripe
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.tenant import Tenant

stripe.api_key = settings.STRIPE_SECRET_KEY


async def create_checkout_session(
    tenant_id: UUID,
    plan: str,
    db: AsyncSession,
    success_url: str = "http://localhost:3000/settings/billing?success=true",
    cancel_url: str = "http://localhost:3000/settings/billing?canceled=true",
) -> str:
    """Cria uma sessão de checkout do Stripe e retorna a URL."""
    tenant = await db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")

    price_id = settings.STRIPE_PRICE_PRO if plan == "pro" else settings.STRIPE_PRICE_PREMIUM

    # Cria ou reutiliza customer
    if not tenant.stripe_customer_id:
        customer = stripe.Customer.create(
            metadata={"tenant_id": str(tenant_id)},
        )
        tenant.stripe_customer_id = customer.id
        await db.flush()

    session = stripe.checkout.Session.create(
        customer=tenant.stripe_customer_id,
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"tenant_id": str(tenant_id), "plan": plan},
    )

    return session.url  # type: ignore[return-value]


async def create_portal_session(tenant_id: UUID, db: AsyncSession) -> str:
    """Cria sessão do Stripe Customer Portal para gestão de assinatura."""
    tenant = await db.get(Tenant, tenant_id)
    if not tenant or not tenant.stripe_customer_id:
        raise HTTPException(status_code=400, detail="Nenhuma assinatura ativa")

    session = stripe.billing_portal.Session.create(
        customer=tenant.stripe_customer_id,
        return_url="http://localhost:3000/settings/billing",
    )
    return session.url


async def get_subscription_status(tenant_id: UUID, db: AsyncSession) -> dict:
    """Retorna status atual da assinatura."""
    tenant = await db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")

    return {
        "plan": tenant.plan,
        "subscription_status": tenant.subscription_status,
        "stripe_customer_id": tenant.stripe_customer_id,
        "stripe_subscription_id": tenant.stripe_subscription_id,
    }


async def handle_checkout_completed(session: dict, db: AsyncSession) -> None:
    """Ativa o plano após checkout bem-sucedido."""
    tenant_id = session.get("metadata", {}).get("tenant_id")
    plan = session.get("metadata", {}).get("plan", "pro")
    subscription_id = session.get("subscription")

    if not tenant_id:
        return

    tenant = await db.get(Tenant, UUID(tenant_id))
    if tenant:
        tenant.plan = plan
        tenant.stripe_subscription_id = subscription_id
        tenant.subscription_status = "active"
        await db.flush()


async def handle_subscription_updated(subscription: dict, db: AsyncSession) -> None:
    """Atualiza status da assinatura."""
    customer_id = subscription.get("customer")
    if not customer_id:
        return

    tenant = await db.scalar(
        select(Tenant).where(Tenant.stripe_customer_id == customer_id)
    )
    if tenant:
        status_map = {
            "active": "active",
            "past_due": "past_due",
            "canceled": "canceled",
            "unpaid": "past_due",
        }
        stripe_status = subscription.get("status", "active")
        tenant.subscription_status = status_map.get(stripe_status, "active")
        await db.flush()


async def handle_subscription_deleted(subscription: dict, db: AsyncSession) -> None:
    """Volta o tenant para o plano free ao cancelar."""
    customer_id = subscription.get("customer")
    if not customer_id:
        return

    tenant = await db.scalar(
        select(Tenant).where(Tenant.stripe_customer_id == customer_id)
    )
    if tenant:
        tenant.plan = "free"
        tenant.subscription_status = "canceled"
        tenant.stripe_subscription_id = None
        await db.flush()
