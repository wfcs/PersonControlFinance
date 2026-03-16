"""Endpoints de billing e assinatura (Stripe)."""

from __future__ import annotations

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.core.deps import AuthUser, DBSession
from app.services import stripe_service

router = APIRouter(prefix="/billing", tags=["Billing"])


class CheckoutRequest(BaseModel):
    plan: str  # "pro" | "premium"
    success_url: str | None = None
    cancel_url: str | None = None


class UrlResponse(BaseModel):
    url: str


@router.post("/checkout", response_model=UrlResponse)
async def create_checkout(
    data: CheckoutRequest, current_user: AuthUser, db: DBSession
) -> UrlResponse:
    """Cria sessão de checkout Stripe para upgrade de plano."""
    url = await stripe_service.create_checkout_session(
        tenant_id=current_user.tenant_id,
        plan=data.plan,
        db=db,
        **({"success_url": data.success_url} if data.success_url else {}),
        **({"cancel_url": data.cancel_url} if data.cancel_url else {}),
    )
    return UrlResponse(url=url)


@router.post("/portal", response_model=UrlResponse)
async def create_portal(current_user: AuthUser, db: DBSession) -> UrlResponse:
    """Redireciona para Stripe Customer Portal."""
    url = await stripe_service.create_portal_session(current_user.tenant_id, db)
    return UrlResponse(url=url)


@router.get("/subscription")
async def get_subscription(current_user: AuthUser, db: DBSession) -> dict:
    """Status atual da assinatura do tenant."""
    return await stripe_service.get_subscription_status(current_user.tenant_id, db)
