"""Tests for the Webhooks API endpoints."""

import pytest
from httpx import AsyncClient

WEBHOOKS_URL = "/api/v1/webhooks/pluggy"


@pytest.mark.asyncio
async def test_pluggy_webhook_receives_event(client: AsyncClient):
    """Webhook endpoint should accept a Pluggy event and return 200."""
    resp = await client.post(
        WEBHOOKS_URL,
        json={
            "event": "ITEM_UPDATED",
            "itemId": "some-item-id-123",
            "data": {"status": "UPDATED"},
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["detail"] == "Webhook received"
    assert "webhook_log_id" in data
