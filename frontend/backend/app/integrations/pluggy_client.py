"""Async wrapper para a API REST do Pluggy (Open Finance)."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

PLUGGY_BASE_URL = "https://api.pluggy.ai"


class PluggyClient:
    """Client HTTP assíncrono com cache automático da API key (TTL ~1h50m)."""

    def __init__(self) -> None:
        self._api_key: str | None = None
        self._api_key_expires_at: datetime | None = None
        self._http = httpx.AsyncClient(base_url=PLUGGY_BASE_URL, timeout=30.0)

    # ── Auth ─────────────────────────────────────────────────────────────────

    async def _ensure_api_key(self) -> str:
        now = datetime.now(timezone.utc)
        if self._api_key and self._api_key_expires_at and now < self._api_key_expires_at:
            return self._api_key

        resp = await self._http.post(
            "/auth",
            json={
                "clientId": settings.PLUGGY_CLIENT_ID,
                "clientSecret": settings.PLUGGY_CLIENT_SECRET,
            },
        )
        resp.raise_for_status()
        self._api_key = resp.json()["apiKey"]
        self._api_key_expires_at = now + timedelta(hours=1, minutes=50)
        return self._api_key  # type: ignore[return-value]

    async def _headers(self) -> dict[str, str]:
        key = await self._ensure_api_key()
        return {"X-API-KEY": key, "Content-Type": "application/json"}

    # ── Connect Token ────────────────────────────────────────────────────────

    async def create_connect_token(
        self,
        item_id: str | None = None,
        webhook_url: str | None = None,
        client_user_id: str | None = None,
    ) -> dict:
        """POST /connect_token — gera token para o widget Pluggy Connect."""
        headers = await self._headers()
        body: dict = {}
        if item_id:
            body["itemId"] = item_id
        if client_user_id:
            body["clientUserId"] = client_user_id
        if webhook_url:
            body["options"] = {"webhookUrl": webhook_url}
        resp = await self._http.post("/connect_token", json=body, headers=headers)
        resp.raise_for_status()
        return resp.json()

    # ── Items ────────────────────────────────────────────────────────────────

    async def get_item(self, item_id: str) -> dict:
        """GET /items/{item_id}"""
        headers = await self._headers()
        resp = await self._http.get(f"/items/{item_id}", headers=headers)
        resp.raise_for_status()
        return resp.json()

    async def delete_item(self, item_id: str) -> None:
        """DELETE /items/{item_id}"""
        headers = await self._headers()
        resp = await self._http.delete(f"/items/{item_id}", headers=headers)
        resp.raise_for_status()

    # ── Accounts ─────────────────────────────────────────────────────────────

    async def get_accounts(self, item_id: str) -> list[dict]:
        """GET /accounts?itemId={item_id}"""
        headers = await self._headers()
        resp = await self._http.get("/accounts", params={"itemId": item_id}, headers=headers)
        resp.raise_for_status()
        return resp.json()["results"]

    # ── Transactions ─────────────────────────────────────────────────────────

    async def get_transactions(
        self,
        account_id: str,
        date_from: str | None = None,
        date_to: str | None = None,
        page: int = 1,
        page_size: int = 500,
    ) -> dict:
        """GET /transactions?accountId=...&from=...&to=..."""
        headers = await self._headers()
        params: dict = {"accountId": account_id, "page": page, "pageSize": page_size}
        if date_from:
            params["from"] = date_from
        if date_to:
            params["to"] = date_to
        resp = await self._http.get("/transactions", params=params, headers=headers)
        resp.raise_for_status()
        return resp.json()

    async def get_transactions_by_ids(self, ids: list[str]) -> dict:
        """GET /transactions?ids=id1,id2,..."""
        headers = await self._headers()
        resp = await self._http.get(
            "/transactions", params={"ids": ",".join(ids)}, headers=headers
        )
        resp.raise_for_status()
        return resp.json()

    # ── Lifecycle ────────────────────────────────────────────────────────────

    async def close(self) -> None:
        await self._http.aclose()


pluggy_client = PluggyClient()
