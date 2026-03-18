from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, FlexibleJSON, FlexibleUUID, TimestampMixin, UUIDPrimaryKeyMixin


class WebhookLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "webhook_logs"

    source: Mapped[str] = mapped_column(String(100), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict] = mapped_column(FlexibleJSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="received", nullable=False)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        FlexibleUUID, ForeignKey("tenants.id"), nullable=False, index=True
    )
