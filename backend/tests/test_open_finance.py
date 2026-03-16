"""Testes para endpoints de Open Finance (Pluggy)."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_connect_token(auth_client: dict):
    client: AsyncClient = auth_client["client"]
    with patch("app.services.pluggy_service.pluggy_client") as mock:
        mock.create_connect_token = AsyncMock(return_value={"accessToken": "tok_123"})
        res = await client.post("/api/v1/open-finance/connect-token", json={})
    assert res.status_code == 200
    assert res.json()["access_token"] == "tok_123"


@pytest.mark.asyncio
async def test_create_connect_token_with_item_id(auth_client: dict):
    client: AsyncClient = auth_client["client"]
    with patch("app.services.pluggy_service.pluggy_client") as mock:
        mock.create_connect_token = AsyncMock(return_value={"accessToken": "tok_456"})
        res = await client.post(
            "/api/v1/open-finance/connect-token", json={"item_id": "item_abc"}
        )
    assert res.status_code == 200
    assert res.json()["access_token"] == "tok_456"


@pytest.mark.asyncio
async def test_trigger_sync(auth_client: dict, sample_account: dict):
    client: AsyncClient = auth_client["client"]
    with patch("app.services.pluggy_service.pluggy_client") as mock:
        mock.get_accounts = AsyncMock(return_value=[])
        mock.get_transactions = AsyncMock(
            return_value={"results": [], "totalPages": 1, "page": 1}
        )
        res = await client.post("/api/v1/open-finance/sync/item_xyz")
    assert res.status_code == 200
    data = res.json()
    assert "accounts_synced" in data
    assert "transactions_synced" in data


@pytest.mark.asyncio
async def test_disconnect_item_not_found(auth_client: dict):
    client: AsyncClient = auth_client["client"]
    res = await client.delete("/api/v1/open-finance/items/nonexistent")
    assert res.status_code == 404
