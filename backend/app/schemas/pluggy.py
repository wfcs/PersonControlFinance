from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ConnectTokenRequest(BaseModel):
    item_id: Optional[str] = None


class ConnectTokenResponse(BaseModel):
    access_token: str


class ItemConnectedRequest(BaseModel):
    item_id: str


class SyncResponse(BaseModel):
    accounts_synced: int
    transactions_imported: int


class PluggyStatusResponse(BaseModel):
    configured: bool
    connected_items: int
