from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, FlexibleJSON, TimestampMixin, UUIDPrimaryKeyMixin


class Plan(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "plans"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    price_monthly: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), nullable=False
    )
    price_yearly: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), nullable=False
    )
    max_connections: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    max_accounts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    features: Mapped[dict] = mapped_column(FlexibleJSON, default=dict, nullable=False)
