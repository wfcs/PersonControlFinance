from __future__ import annotations

import logging
import os
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant

logger = logging.getLogger(__name__)

# Map Stripe price IDs to plans (configured at startup)
PRICE_TO_PLAN: dict[str, str] = {}


def _get_stripe():
    """Lazy import stripe to avoid import errors when not installed."""
    if os.environ.get("TESTING") == "1":
        return None
    try:
        import stripe
        from app.core.config import settings
        stripe.api_key = settings.STRIPE_SECRET_KEY
        return stripe
    except ImportError:
        return None


def init_price_mapping():
    """Initialize price-to-plan mapping from settings."""
    from app.core.config import settings
    if settings.STRIPE_PRICE_PRO_MONTHLY:
        PRICE_TO_PLAN[settings.STRIPE_PRICE_PRO_MONTHLY] = "pro"
    if settings.STRIPE_PRICE_PRO_ANNUAL:
        PRICE_TO_PLAN[settings.STRIPE_PRICE_PRO_ANNUAL] = "pro"
    if settings.STRIPE_PRICE_PREMIUM_MONTHLY:
        PRICE_TO_PLAN[settings.STRIPE_PRICE_PREMIUM_MONTHLY] = "premium"
    if settings.STRIPE_PRICE_PREMIUM_ANNUAL:
        PRICE_TO_PLAN[settings.STRIPE_PRICE_PREMIUM_ANNUAL] = "premium"


async def get_tenant(tenant_id: UUID, session: AsyncSession) -> Tenant:
    result = await session.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return tenant


async def ensure_stripe_customer(
    tenant: Tenant, email: str, session: AsyncSession
) -> str:
    """Ensure tenant has a Stripe customer, create one if not."""
    if tenant.stripe_customer_id:
        return tenant.stripe_customer_id

    stripe = _get_stripe()
    if stripe is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe not configured",
        )

    customer = stripe.Customer.create(
        email=email,
        name=tenant.name,
        metadata={"tenant_id": str(tenant.id)},
    )
    tenant.stripe_customer_id = customer.id
    await session.flush()
    return customer.id


async def create_checkout_session(
    tenant_id: UUID,
    email: str,
    price_id: str,
    success_url: str,
    cancel_url: str,
    session: AsyncSession,
) -> str:
    """Create Stripe Checkout Session and return URL."""
    stripe = _get_stripe()
    if stripe is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe not configured",
        )

    tenant = await get_tenant(tenant_id, session)
    customer_id = await ensure_stripe_customer(tenant, email, session)

    checkout = stripe.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"tenant_id": str(tenant_id)},
    )
    return checkout.url


async def create_portal_session(
    tenant_id: UUID,
    return_url: str,
    session: AsyncSession,
) -> str:
    """Create Stripe Customer Portal session."""
    stripe = _get_stripe()
    if stripe is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe not configured",
        )

    tenant = await get_tenant(tenant_id, session)
    if not tenant.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No billing account found. Subscribe to a plan first.",
        )

    portal = stripe.billing_portal.Session.create(
        customer=tenant.stripe_customer_id,
        return_url=return_url,
    )
    return portal.url


async def handle_webhook_event(
    event_type: str, data: dict, session: AsyncSession
) -> None:
    """Process Stripe webhook events to update tenant plan."""
    obj = data.get("object", {})

    if event_type in (
        "customer.subscription.created",
        "customer.subscription.updated",
    ):
        customer_id = obj.get("customer")
        sub_status = obj.get("status")  # active, past_due, canceled, etc.
        sub_id = obj.get("id")

        # Get price_id from first item
        items = obj.get("items", {}).get("data", [])
        price_id = items[0]["price"]["id"] if items else None
        plan = PRICE_TO_PLAN.get(price_id, "free") if price_id else "free"

        # Find tenant
        result = await session.execute(
            select(Tenant).where(Tenant.stripe_customer_id == customer_id)
        )
        tenant = result.scalar_one_or_none()
        if tenant is None:
            logger.warning("No tenant found for Stripe customer %s", customer_id)
            return

        tenant.plan = plan if sub_status == "active" else "free"
        tenant.subscription_status = sub_status
        tenant.stripe_subscription_id = sub_id
        await session.flush()
        logger.info(
            "Tenant %s updated: plan=%s status=%s", tenant.id, tenant.plan, sub_status
        )

    elif event_type == "customer.subscription.deleted":
        customer_id = obj.get("customer")
        result = await session.execute(
            select(Tenant).where(Tenant.stripe_customer_id == customer_id)
        )
        tenant = result.scalar_one_or_none()
        if tenant:
            tenant.plan = "free"
            tenant.subscription_status = "canceled"
            tenant.stripe_subscription_id = None
            await session.flush()
            logger.info("Tenant %s downgraded to free (subscription deleted)", tenant.id)

    elif event_type == "checkout.session.completed":
        # Subscription already handled by subscription events
        logger.info("Checkout completed for customer %s", obj.get("customer"))
