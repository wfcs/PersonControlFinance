"""Schemas para integração Pluggy (Open Finance)."""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel


class ConnectTokenRequest(BaseModel):
    item_id: str | None = None  # Para reconectar item existente


class ConnectTokenResponse(BaseModel):
    access_token: str


class PluggyWebhookPayload(BaseModel):
    """Payload recebido dos webhooks do Pluggy (já convertido de camelCase)."""

    event: str
    event_id: str | None = None
    item_id: str | None = None
    account_id: str | None = None
    triggered_by: str | None = None
    client_user_id: str | None = None
    transactions_count: int | None = None
    created_transactions_link: str | None = None
    transaction_ids: list[str] | None = None


class SyncStatusOut(BaseModel):
    item_id: str
    status: str
    last_sync: datetime | None
    accounts_synced: int
    transactions_synced: int
