from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AccountCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    type: str = Field(min_length=1, max_length=50)
    bank_name: Optional[str] = None
    balance: Decimal = Decimal("0.00")
    currency: str = Field(default="BRL", max_length=3)


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    bank_name: Optional[str] = None
    balance: Optional[Decimal] = None
    currency: Optional[str] = None


class AccountResponse(BaseModel):
    id: UUID
    name: str
    type: str
    bank_name: Optional[str]
    balance: Decimal
    currency: str
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
