"""Pydantic schemas for Transaction endpoints."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Generic, Literal, Optional, TypeVar

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    description: str = Field(min_length=1, max_length=500)
    amount: Decimal = Field(gt=0)
    type: Literal["income", "expense"]
    date: date
    account_id: uuid.UUID
    category_id: Optional[uuid.UUID] = None
    is_recurring: bool = False
    notes: Optional[str] = None


class TransactionUpdate(BaseModel):
    description: Optional[str] = Field(default=None, min_length=1, max_length=500)
    amount: Optional[Decimal] = Field(default=None, gt=0)
    type: Optional[Literal["income", "expense"]] = None
    date: Optional[date] = None
    account_id: Optional[uuid.UUID] = None
    category_id: Optional[uuid.UUID] = None
    is_recurring: Optional[bool] = None
    notes: Optional[str] = None


class TransactionRead(BaseModel):
    id: uuid.UUID
    description: str
    amount: Decimal
    type: str
    date: date
    is_recurring: bool
    notes: Optional[str]
    account_id: uuid.UUID
    category_id: Optional[uuid.UUID]
    tenant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    category_name: Optional[str] = None
    account_name: Optional[str] = None

    model_config = {"from_attributes": True}


class TransactionFilters(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    account_id: Optional[uuid.UUID] = None
    category_id: Optional[uuid.UUID] = None
    type: Optional[Literal["income", "expense"]] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    search: Optional[str] = None


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
