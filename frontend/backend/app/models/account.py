import uuid
from decimal import Decimal

from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TenantMixin, TimestampMixin


class Account(Base, TenantMixin, TimestampMixin):
    """Conta bancária ou cartão de crédito conectado via Open Finance."""

    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    institution_name: Mapped[str] = mapped_column(String(120), nullable=False)
    institution_logo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    # checking | savings | credit_card | investment | wallet

    # Open Finance
    pluggy_item_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    pluggy_account_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)

    # Saldos
    balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    credit_limit: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    tenant: Mapped["Tenant"] = relationship(back_populates="accounts")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="account")
