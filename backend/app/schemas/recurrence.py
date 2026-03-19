from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RecurrenceCreate(BaseModel):
    description: str = Field(min_length=1, max_length=500)
    amount: Decimal
    type: str = Field(min_length=1, max_length=50)
    frequency: str = Field(min_length=1, max_length=50)
    next_due_date: date
    account_id: UUID
    category_id: Optional[UUID] = None
    is_active: bool = True


class RecurrenceUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    type: Optional[str] = None
    frequency: Optional[str] = None
    next_due_date: Optional[date] = None
    account_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class RecurrenceResponse(BaseModel):
    id: UUID
    description: str
    amount: Decimal
    type: str
    frequency: str
    next_due_date: date
    account_id: UUID
    category_id: Optional[UUID]
    tenant_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
