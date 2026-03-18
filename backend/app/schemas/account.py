"""Pydantic schemas for Account endpoints."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field


class AccountCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    type: Literal["checking", "savings", "credit_card", "investment"]
    institution: Optional[str] = Field(default=None, max_length=255)
    balance: Decimal = Decimal("0.00")
    currency: str = Field(default="BRL", max_length=3)


class AccountUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    type: Optional[Literal["checking", "savings", "credit_card", "investment"]] = None
    institution: Optional[str] = None
    balance: Optional[Decimal] = None
    currency: Optional[str] = Field(default=None, max_length=3)


class AccountRead(BaseModel):
    id: uuid.UUID
    name: str
    type: str
    institution: Optional[str]
    balance: Decimal
    currency: str
    pluggy_account_id: Optional[str]
    tenant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PluggyConnectRequest(BaseModel):
    item_id: Optional[str] = None


class PluggyConnectResponse(BaseModel):
    connect_token: str
