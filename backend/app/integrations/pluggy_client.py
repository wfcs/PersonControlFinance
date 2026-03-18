"""Pluggy Open Finance API client."""

from __future__ import annotations

import logging
from datetime import date

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

PLUGGY_BASE_URL = "https://api.pluggy.ai"


class PluggyClient:
    """Async client for the Pluggy Open Finance API."""

    def __init__(self) -> None:
        self._token: str | None = None

    async def authenticate(self) -> str | None:
        """Obtain an API token from Pluggy using client credentials."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{PLUGGY_BASE_URL}/auth",
                    json={
                        "clientId": settings.PLUGGY_CLIENT_ID,
                        "clientSecret": settings.PLUGGY_CLIENT_SECRET,
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()
                self._token = data.get("apiKey")
                return self._token
        except Exception:
            logger.exception("Failed to authenticate with Pluggy")
            return None

    def _headers(self) -> dict[str, str]:
        return {
            "X-API-KEY": self._token or "",
            "Content-Type": "application/json",
        }

    async def create_connect_token(self, item_id: str | None = None) -> str | None:
        """Create a connect token for the Pluggy Connect widget."""
        if not self._token:
            await self.authenticate()
        try:
            body: dict = {}
            if item_id:
                body["itemId"] = item_id
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{PLUGGY_BASE_URL}/connect_token",
                    json=body,
                    headers=self._headers(),
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("accessToken")
        except Exception:
            logger.exception("Failed to create Pluggy connect token")
            return None

    async def get_accounts(self, item_id: str) -> list[dict]:
        """List accounts from a Pluggy connection (item)."""
        if not self._token:
            await self.authenticate()
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{PLUGGY_BASE_URL}/accounts",
                    params={"itemId": item_id},
                    headers=self._headers(),
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("results", [])
        except Exception:
            logger.exception("Failed to get accounts from Pluggy")
            return []

    async def get_transactions(
        self,
        account_id: str,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[dict]:
        """List transactions for a Pluggy account."""
        if not self._token:
            await self.authenticate()
        try:
            params: dict = {"accountId": account_id}
            if from_date:
                params["from"] = from_date.isoformat()
            if to_date:
                params["to"] = to_date.isoformat()
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{PLUGGY_BASE_URL}/transactions",
                    params=params,
                    headers=self._headers(),
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("results", [])
        except Exception:
            logger.exception("Failed to get transactions from Pluggy")
            return []

    async def get_item(self, item_id: str) -> dict | None:
        """Get a connection (item) status from Pluggy."""
        if not self._token:
            await self.authenticate()
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{PLUGGY_BASE_URL}/items/{item_id}",
                    headers=self._headers(),
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except Exception:
            logger.exception("Failed to get item from Pluggy")
            return None
