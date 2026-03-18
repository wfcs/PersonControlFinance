"""Category model with optional self-referencing parent (sub-categories)."""

import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        Index("ix_categories_tenant_id_id", "tenant_id", "id"),
        Index("ix_categories_tenant_id_type", "tenant_id", "type"),
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)  # hex color
    type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # income / expense
    budget_limit: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=18, scale=2), nullable=True
    )

    # ── self-referencing parent ──────────────────────────────
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    children: Mapped[list["Category"]] = relationship(
        back_populates="parent", lazy="selectin"
    )
    parent: Mapped["Category | None"] = relationship(
        back_populates="children", remote_side="Category.id"
    )

    # ── tenant FK ────────────────────────────────────────────
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tenant: Mapped["Tenant"] = relationship(back_populates="categories")  # noqa: F821

    # ── relationships ────────────────────────────────────────
    transactions: Mapped[list["Transaction"]] = relationship(  # noqa: F821
        back_populates="category", lazy="selectin"
    )
    recurrences: Mapped[list["Recurrence"]] = relationship(  # noqa: F821
        back_populates="category", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Category {self.name}>"
