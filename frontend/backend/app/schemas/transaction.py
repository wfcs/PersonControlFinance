from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class TransactionCreate(BaseModel):
    account_id: UUID
    category_id: UUID | None = None
    description: str
    amount: Decimal
    type: str
    date: datetime
    notes: str | None = None


class TransactionUpdate(BaseModel):
    category_id: UUID | None = None
    description: str | None = None
    notes: str | None = None
    is_excluded: bool | None = None


class TransactionOut(BaseModel):
    id: UUID
    account_id: UUID
    category_id: UUID | None
    description: str
    amount: Decimal
    type: str
    date: datetime
    notes: str | None
    is_excluded: bool
    installment_number: int | None
    installment_total: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionListResponse(BaseModel):
    items: list[TransactionOut]
    total: int
    page: int
    page_size: int
