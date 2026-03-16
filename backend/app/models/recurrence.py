import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TenantMixin, TimestampMixin


class Recurrence(Base, TenantMixin, TimestampMixin):
    """Parcelas detectadas e contas fixas recorrentes."""

    __tablename__ = "recurrences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description: Mapped[str] = mapped_column(String(256), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )

    frequency: Mapped[str] = mapped_column(String(20), nullable=False)
    # monthly | weekly | yearly | installment

    # Para parcelas
    total_installments: Mapped[int | None] = mapped_column(nullable=True)
    current_installment: Mapped[int | None] = mapped_column(nullable=True)
    next_due_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="recurrence")
    tenant: Mapped["Tenant"] = relationship(back_populates="recurrences")
