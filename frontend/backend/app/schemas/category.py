from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    icon: str | None = None
    color: str | None = None
    monthly_limit: Decimal | None = None
    parent_id: UUID | None = None


class CategoryUpdate(BaseModel):
    name: str | None = None
    icon: str | None = None
    color: str | None = None
    monthly_limit: Decimal | None = None


class CategoryOut(BaseModel):
    id: UUID
    name: str
    icon: str | None
    color: str | None
    monthly_limit: Decimal | None
    parent_id: UUID | None
    children: list["CategoryOut"] = []

    model_config = {"from_attributes": True}
