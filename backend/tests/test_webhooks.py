from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_pluggy_webhook_received(client: AsyncClient) -> None:
    tenant_id = str(uuid.uuid4())
    resp = await client.post(
        "/api/v1/webhooks/pluggy",
        json={
            "event": "item/updated",
            "tenant_id": tenant_id,
            "data": {"item_id": "abc123"},
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "received"
    assert data["event"] == "item/updated"


@pytest.mark.asyncio
async def test_pluggy_webhook_no_tenant(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/webhooks/pluggy",
        json={"event": "test/ping", "data": {}},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "received"
