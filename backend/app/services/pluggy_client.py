from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

PLUGGY_BASE_URL = "https://api.pluggy.ai"

# Cached token
_token_cache: dict[str, Any] = {"token": None, "expires_at": None}


def _is_configured() -> bool:
    """Check if Pluggy credentials are configured."""
    return bool(settings.PLUGGY_CLIENT_ID and settings.PLUGGY_CLIENT_SECRET)


async def _get_api_key() -> str:
    """Authenticate with Pluggy and return an API key (cached)."""
    now = datetime.utcnow()
    if _token_cache["token"] and _token_cache["expires_at"] and _token_cache["expires_at"] > now:
        return _token_cache["token"]

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{PLUGGY_BASE_URL}/auth",
            json={
                "clientId": settings.PLUGGY_CLIENT_ID,
                "clientSecret": settings.PLUGGY_CLIENT_SECRET,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    _token_cache["token"] = data["apiKey"]
    # Pluggy tokens last 2 hours, cache for 1h50
    _token_cache["expires_at"] = now + timedelta(hours=1, minutes=50)
    return data["apiKey"]


async def _headers() -> dict[str, str]:
    api_key = await _get_api_key()
    return {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }


async def create_connect_token(item_id: Optional[str] = None) -> str:
    """Create a connect token for the Pluggy Connect Widget.

    If item_id is provided, creates an update token for an existing item.
    """
    if not _is_configured():
        raise RuntimeError("Pluggy not configured")

    body: dict[str, Any] = {}
    if item_id:
        body["itemId"] = item_id

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{PLUGGY_BASE_URL}/connect_token",
            headers=await _headers(),
            json=body,
        )
        resp.raise_for_status()
        return resp.json()["accessToken"]


async def get_item(item_id: str) -> dict[str, Any]:
    """Get a Pluggy item (bank connection) by ID."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{PLUGGY_BASE_URL}/items/{item_id}",
            headers=await _headers(),
        )
        resp.raise_for_status()
        return resp.json()


async def get_item_accounts(item_id: str) -> list[dict[str, Any]]:
    """Get all accounts for a Pluggy item."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{PLUGGY_BASE_URL}/accounts",
            headers=await _headers(),
            params={"itemId": item_id},
        )
        resp.raise_for_status()
        return resp.json().get("results", [])


async def get_account_transactions(
    account_id: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = 1,
    page_size: int = 500,
) -> dict[str, Any]:
    """Get transactions for a Pluggy account."""
    params: dict[str, Any] = {
        "accountId": account_id,
        "page": page,
        "pageSize": page_size,
    }
    if date_from:
        params["from"] = date_from
    if date_to:
        params["to"] = date_to

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{PLUGGY_BASE_URL}/transactions",
            headers=await _headers(),
            params=params,
        )
        resp.raise_for_status()
        return resp.json()


async def delete_item(item_id: str) -> None:
    """Delete a Pluggy item (disconnect bank)."""
    async with httpx.AsyncClient() as client:
        resp = await client.delete(
            f"{PLUGGY_BASE_URL}/items/{item_id}",
            headers=await _headers(),
        )
        resp.raise_for_status()
