from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class AccountOut(BaseModel):
    id: UUID
    name: str
    institution_name: str
    institution_logo_url: str | None
    type: str
    balance: Decimal
    credit_limit: Decimal | None
    is_active: bool
    pluggy_item_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AccountCreate(BaseModel):
    name: str
    institution_name: str
    type: str
    balance: Decimal = Decimal("0")
    credit_limit: Decimal | None = None


class AccountUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None
