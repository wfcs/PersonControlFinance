"""Pydantic schemas for Goal endpoints."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, computed_field


class GoalCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    target_amount: Decimal = Field(gt=0)
    deadline: Optional[date] = None
    category_id: Optional[uuid.UUID] = None


class GoalUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    target_amount: Optional[Decimal] = Field(default=None, gt=0)
    current_amount: Optional[Decimal] = Field(default=None, ge=0)
    deadline: Optional[date] = None
    status: Optional[str] = None


class GoalRead(BaseModel):
    id: uuid.UUID
    name: str
    target_amount: Decimal
    current_amount: Decimal
    deadline: Optional[date]
    status: str
    tenant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    @computed_field  # type: ignore[prop-decorator]
    @property
    def progress(self) -> float:
        if self.target_amount == 0:
            return 100.0
        return round(float(self.current_amount / self.target_amount * 100), 2)

    model_config = {"from_attributes": True}
