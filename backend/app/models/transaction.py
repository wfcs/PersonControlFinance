"""Transaction model."""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        Index("ix_transactions_tenant_id_id", "tenant_id", "id"),
        Index("ix_transactions_tenant_id_date", "tenant_id", "date"),
        Index("ix_transactions_tenant_id_type", "tenant_id", "type"),
        Index("ix_transactions_tenant_id_account_id", "tenant_id", "account_id"),
    )

    description: Mapped[str] = mapped_column(String(500), nullable=False)
    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=2), nullable=False
    )
    type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # income / expense
    date: Mapped[date] = mapped_column(Date, nullable=False)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── FKs ──────────────────────────────────────────────────
    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    account: Mapped["Account"] = relationship(back_populates="transactions")  # noqa: F821

    category_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    category: Mapped["Category | None"] = relationship(back_populates="transactions")  # noqa: F821

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tenant: Mapped["Tenant"] = relationship(back_populates="transactions")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Transaction {self.description} {self.amount}>"
