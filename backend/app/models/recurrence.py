"""Recurrence model (recurring bills, subscriptions)."""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Recurrence(Base):
    __tablename__ = "recurrences"

    description: Mapped[str] = mapped_column(String(500), nullable=False)
    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=2), nullable=False
    )
    type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # income / expense
    frequency: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # monthly, weekly, yearly
    next_due_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # ── FKs ──────────────────────────────────────────────────
    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    account: Mapped["Account"] = relationship(back_populates="recurrences")  # noqa: F821

    category_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    category: Mapped["Category | None"] = relationship(back_populates="recurrences")  # noqa: F821

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tenant: Mapped["Tenant"] = relationship(back_populates="recurrences")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Recurrence {self.description} ({self.frequency})>"
