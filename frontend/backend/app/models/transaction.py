import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TenantMixin, TimestampMixin


class Transaction(Base, TenantMixin, TimestampMixin):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )

    description: Mapped[str] = mapped_column(String(256), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    # positivo = receita, negativo = despesa
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    # debit | credit | transfer | pix

    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Open Finance
    external_id: Mapped[str | None] = mapped_column(String(120), nullable=True, unique=True, index=True)

    # Recorrências / parcelas
    recurrence_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("recurrences.id", ondelete="SET NULL"), nullable=True
    )
    installment_number: Mapped[int | None] = mapped_column(nullable=True)
    installment_total: Mapped[int | None] = mapped_column(nullable=True)

    is_excluded: Mapped[bool] = mapped_column(nullable=False, default=False)

    account: Mapped["Account"] = relationship(back_populates="transactions")
    category: Mapped["Category | None"] = relationship(back_populates="transactions")
    recurrence: Mapped["Recurrence | None"] = relationship(back_populates="transactions")
    tenant: Mapped["Tenant"] = relationship(back_populates="transactions")
