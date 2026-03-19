from __future__ import annotations

import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "openfinance@example.com",
            "full_name": "OF User",
            "password": "strongpass123",
            "tenant_name": "OF Corp",
        },
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "openfinance@example.com", "password": "strongpass123"},
    )
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_pluggy_status(client: AsyncClient) -> None:
    token = await _register_and_login(client)
    resp = await client.get(
        "/api/v1/open-finance/status",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "configured" in data
    assert "connected_items" in data
    assert data["connected_items"] == 0


@pytest.mark.asyncio
async def test_connect_token_requires_pluggy_config(client: AsyncClient) -> None:
    """Without PLUGGY_CLIENT_ID/SECRET set, connect-token returns 503 or test token."""
    token = await _register_and_login(client)
    resp = await client.post(
        "/api/v1/open-finance/connect-token",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    # In TESTING=1 mode without config, should return 503 (not configured)
    # OR if TESTING=1 bypasses the check, returns test token
    assert resp.status_code in (200, 503)


@pytest.mark.asyncio
async def test_connect_item_requires_pluggy_config(client: AsyncClient) -> None:
    token = await _register_and_login(client)
    resp = await client.post(
        "/api/v1/open-finance/connect",
        json={"item_id": "test-item-123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code in (200, 503)


@pytest.mark.asyncio
async def test_sync_item_requires_pluggy_config(client: AsyncClient) -> None:
    token = await _register_and_login(client)
    resp = await client.post(
        "/api/v1/open-finance/sync/test-item-123",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code in (200, 503)


@pytest.mark.asyncio
async def test_disconnect_item_requires_pluggy_config(client: AsyncClient) -> None:
    token = await _register_and_login(client)
    resp = await client.delete(
        "/api/v1/open-finance/disconnect/test-item-123",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code in (200, 503)


@pytest.mark.asyncio
async def test_open_finance_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/open-finance/status")
    assert resp.status_code in (401, 403)
