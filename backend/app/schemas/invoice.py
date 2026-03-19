from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class InvoiceCreate(BaseModel):
    credit_card_account_id: UUID
    due_date: date
    close_date: date
    total_amount: Decimal = Decimal("0.00")
    status: str = Field(default="open", max_length=50)


class InvoiceUpdate(BaseModel):
    due_date: Optional[date] = None
    close_date: Optional[date] = None
    total_amount: Optional[Decimal] = None
    status: Optional[str] = None


class InvoiceResponse(BaseModel):
    id: UUID
    credit_card_account_id: UUID
    due_date: date
    close_date: date
    total_amount: Decimal
    status: str
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
