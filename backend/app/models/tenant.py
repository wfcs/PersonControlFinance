"""Tenant model -- top-level entity for multi-tenancy."""

import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Tenant(Base):
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    plan: Mapped[str] = mapped_column(String(50), nullable=False, default="free")
    subscription_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active"
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ── relationships ────────────────────────────────────────
    users: Mapped[list["User"]] = relationship(  # noqa: F821
        back_populates="tenant", cascade="all, delete-orphan", lazy="selectin"
    )
    accounts: Mapped[list["Account"]] = relationship(  # noqa: F821
        back_populates="tenant", cascade="all, delete-orphan", lazy="selectin"
    )
    categories: Mapped[list["Category"]] = relationship(  # noqa: F821
        back_populates="tenant", cascade="all, delete-orphan", lazy="selectin"
    )
    transactions: Mapped[list["Transaction"]] = relationship(  # noqa: F821
        back_populates="tenant", cascade="all, delete-orphan", lazy="selectin"
    )
    goals: Mapped[list["Goal"]] = relationship(  # noqa: F821
        back_populates="tenant", cascade="all, delete-orphan", lazy="selectin"
    )
    recurrences: Mapped[list["Recurrence"]] = relationship(  # noqa: F821
        back_populates="tenant", cascade="all, delete-orphan", lazy="selectin"
    )
    webhook_logs: Mapped[list["WebhookLog"]] = relationship(  # noqa: F821
        back_populates="tenant", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Tenant {self.slug}>"
