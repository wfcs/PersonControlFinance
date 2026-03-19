from __future__ import annotations

import os

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.billing import (
    CreateCheckoutRequest,
    CreateCheckoutResponse,
    CreatePortalRequest,
    CreatePortalResponse,
    SubscriptionStatusResponse,
)
from app.services.billing_service import (
    create_checkout_session,
    create_portal_session,
    get_tenant,
    handle_webhook_event,
)

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.get("/status", response_model=SubscriptionStatusResponse)
async def subscription_status(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SubscriptionStatusResponse:
    """Get current subscription status."""
    tenant = await get_tenant(current_user.tenant_id, session)
    return SubscriptionStatusResponse(
        tenant_id=tenant.id,
        plan=tenant.plan,
        subscription_status=tenant.subscription_status,
        stripe_customer_id=tenant.stripe_customer_id,
        stripe_subscription_id=tenant.stripe_subscription_id,
    )


@router.post("/checkout", response_model=CreateCheckoutResponse)
async def create_checkout(
    data: CreateCheckoutRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> CreateCheckoutResponse:
    """Create a Stripe Checkout Session for subscription."""
    url = await create_checkout_session(
        tenant_id=current_user.tenant_id,
        email=current_user.email,
        price_id=data.price_id,
        success_url=data.success_url,
        cancel_url=data.cancel_url,
        session=session,
    )
    return CreateCheckoutResponse(checkout_url=url)


@router.post("/portal", response_model=CreatePortalResponse)
async def create_portal(
    data: CreatePortalRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> CreatePortalResponse:
    """Create a Stripe Customer Portal session for managing subscription."""
    url = await create_portal_session(
        tenant_id=current_user.tenant_id,
        return_url=data.return_url,
        session=session,
    )
    return CreatePortalResponse(portal_url=url)


@router.post("/webhook", status_code=200)
async def stripe_webhook(
    request: Request,
    session: AsyncSession = Depends(get_session),
    stripe_signature: str = Header(None, alias="stripe-signature"),
) -> dict:
    """Handle Stripe webhook events."""
    body = await request.body()

    if os.environ.get("TESTING") == "1":
        # In tests, parse body directly without signature verification
        import json
        payload = json.loads(body)
        event_type = payload.get("type", "")
        data = payload.get("data", {})
    else:
        try:
            import stripe
            from app.core.config import settings
            stripe.api_key = settings.STRIPE_SECRET_KEY
            event = stripe.Webhook.construct_event(
                body, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
            )
            event_type = event["type"]
            data = event["data"]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Webhook error: {str(e)}",
            )

    await handle_webhook_event(event_type, data, session)
    return {"status": "ok"}
