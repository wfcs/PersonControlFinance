"""Pydantic schemas for Category endpoints."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    icon: Optional[str] = Field(default=None, max_length=50)
    color: Optional[str] = Field(default=None, max_length=7)
    type: Literal["income", "expense"]
    parent_id: Optional[uuid.UUID] = None
    budget_limit: Optional[Decimal] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    icon: Optional[str] = None
    color: Optional[str] = None
    type: Optional[Literal["income", "expense"]] = None
    parent_id: Optional[uuid.UUID] = None
    budget_limit: Optional[Decimal] = None


class CategoryRead(BaseModel):
    id: uuid.UUID
    name: str
    icon: Optional[str]
    color: Optional[str]
    type: str
    budget_limit: Optional[Decimal]
    parent_id: Optional[uuid.UUID]
    tenant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    subcategories: list["CategoryRead"] = []

    model_config = {"from_attributes": True}
