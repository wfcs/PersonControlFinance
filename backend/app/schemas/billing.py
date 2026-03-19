from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CreateCheckoutRequest(BaseModel):
    price_id: str
    success_url: str = "http://localhost:3000/plans?success=true"
    cancel_url: str = "http://localhost:3000/plans?canceled=true"


class CreateCheckoutResponse(BaseModel):
    checkout_url: str


class CreatePortalRequest(BaseModel):
    return_url: str = "http://localhost:3000/plans"


class CreatePortalResponse(BaseModel):
    portal_url: str


class SubscriptionStatusResponse(BaseModel):
    tenant_id: UUID
    plan: str
    subscription_status: str
    stripe_customer_id: Optional[str]
    stripe_subscription_id: Optional[str]
