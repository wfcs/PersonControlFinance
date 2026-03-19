from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, FlexibleUUID, TimestampMixin, UUIDPrimaryKeyMixin


class Category(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "categories"
    __table_args__ = (
        Index("ix_categories_tenant_id_id", "tenant_id", "id"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        FlexibleUUID, ForeignKey("categories.id"), nullable=True
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        FlexibleUUID, ForeignKey("tenants.id"), nullable=False, index=True
    )

    parent: Mapped[Category | None] = relationship(
        "Category", remote_side="Category.id", lazy="selectin"
    )
