"""Account model (bank accounts, credit cards, investments, etc.)."""

import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        Index("ix_accounts_tenant_id_id", "tenant_id", "id"),
        Index("ix_accounts_tenant_id_type", "tenant_id", "type"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # checking, savings, credit_card, investment
    institution: Mapped[str | None] = mapped_column(String(255), nullable=True)
    balance: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=2), nullable=False, default=Decimal("0.00")
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="BRL")
    pluggy_account_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ── tenant FK ────────────────────────────────────────────
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tenant: Mapped["Tenant"] = relationship(back_populates="accounts")  # noqa: F821

    # ── relationships ────────────────────────────────────────
    transactions: Mapped[list["Transaction"]] = relationship(  # noqa: F821
        back_populates="account", cascade="all, delete-orphan", lazy="selectin"
    )
    recurrences: Mapped[list["Recurrence"]] = relationship(  # noqa: F821
        back_populates="account", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Account {self.name} ({self.type})>"
