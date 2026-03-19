from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    description: str = Field(min_length=1, max_length=500)
    amount: Decimal
    type: str = Field(min_length=1, max_length=50)
    date: date
    account_id: UUID
    category_id: Optional[UUID] = None
    is_recurring: bool = False
    notes: Optional[str] = None


class TransactionUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    type: Optional[str] = None
    date: Optional[date] = None
    account_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    is_recurring: Optional[bool] = None
    notes: Optional[str] = None


class TransactionResponse(BaseModel):
    id: UUID
    description: str
    amount: Decimal
    type: str
    date: date
    account_id: UUID
    category_id: Optional[UUID]
    tenant_id: UUID
    is_recurring: bool
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TransactionFilter(BaseModel):
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    account_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    type: Optional[str] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    search: Optional[str] = None
