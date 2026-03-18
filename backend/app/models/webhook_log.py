"""WebhookLog model -- audit log for incoming webhooks."""

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class WebhookLog(Base):
    __tablename__ = "webhook_logs"

    source: Mapped[str] = mapped_column(String(100), nullable=False)  # stripe, pluggy
    event_type: Mapped[str] = mapped_column(String(200), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="received"
    )  # received, processed, failed

    # ── tenant FK ────────────────────────────────────────────
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("tenants.id", ondelete="SET NULL"), nullable=True, index=True
    )
    tenant: Mapped["Tenant | None"] = relationship(back_populates="webhook_logs")  # noqa: F821

    def __repr__(self) -> str:
        return f"<WebhookLog {self.source}:{self.event_type}>"
