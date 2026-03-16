"""Schemas para recorrências e parcelas."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class RecurrenceOut(BaseModel):
    id: UUID
    description: str
    amount: Decimal
    frequency: str
    total_installments: int | None
    current_installment: int | None
    next_due_date: date | None
    is_active: bool
    category_id: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RecurrenceCreate(BaseModel):
    description: str
    amount: Decimal
    frequency: str
    category_id: UUID | None = None
    total_installments: int | None = None
    next_due_date: date | None = None


class RecurrenceUpdate(BaseModel):
    description: str | None = None
    amount: Decimal | None = None
    category_id: UUID | None = None
    next_due_date: date | None = None
    is_active: bool | None = None
