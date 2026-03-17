"""Testes para webhook handlers."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_pluggy_webhook_item_updated(client: AsyncClient):
    """Webhook de item/updated retorna 200."""
    payload = {
        "event": "item/updated",
        "eventId": "evt_123",
        "itemId": "item_abc",
        "triggeredBy": "SYNC",
        "clientUserId": "00000000-0000-0000-0000-000000000000:user123",
    }
    res = await client.post("/api/v1/webhooks/pluggy", json=payload)
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_pluggy_webhook_transactions_created(client: AsyncClient):
    payload = {
        "event": "transactions/created",
        "eventId": "evt_456",
        "itemId": "item_abc",
        "transactionsCount": 5,
        "clientUserId": "00000000-0000-0000-0000-000000000000:user123",
    }
    res = await client.post("/api/v1/webhooks/pluggy", json=payload)
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_pluggy_webhook_unknown_event(client: AsyncClient):
    """Evento desconhecido é aceito sem erro."""
    payload = {"event": "unknown/event", "eventId": "evt_789"}
    res = await client.post("/api/v1/webhooks/pluggy", json=payload)
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_pluggy_webhook_item_error(client: AsyncClient):
    payload = {
        "event": "item/error",
        "eventId": "evt_err",
        "itemId": "item_broken",
        "clientUserId": "00000000-0000-0000-0000-000000000000:user123",
    }
    res = await client.post("/api/v1/webhooks/pluggy", json=payload)
    assert res.status_code == 200
