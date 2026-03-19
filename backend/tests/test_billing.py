from __future__ import annotations

import json

import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "billing@example.com",
            "full_name": "Billing User",
            "password": "strongpass123",
            "tenant_name": "Billing Corp",
        },
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "billing@example.com", "password": "strongpass123"},
    )
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_billing_status(client: AsyncClient) -> None:
    token = await _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get("/api/v1/billing/status", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["plan"] == "free"
    assert data["subscription_status"] == "active"
    assert data["stripe_customer_id"] is None


@pytest.mark.asyncio
async def test_billing_checkout_no_stripe(client: AsyncClient) -> None:
    """Checkout should return 503 when Stripe is not configured (TESTING=1)."""
    token = await _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.post(
        "/api/v1/billing/checkout",
        json={"price_id": "price_test_123"},
        headers=headers,
    )
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_billing_portal_no_customer(client: AsyncClient) -> None:
    """Portal should return 503 when Stripe is not configured."""
    token = await _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.post(
        "/api/v1/billing/portal",
        json={"return_url": "http://localhost:3000/plans"},
        headers=headers,
    )
    # 503 because Stripe not configured in test mode
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_stripe_webhook_subscription_event(client: AsyncClient, db_session) -> None:
    """Test webhook processing for subscription events."""
    # First register to create a tenant
    await _register_and_login(client)

    # Simulate a Stripe webhook event (testing mode bypasses signature)
    event_payload = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "customer": "cus_test_123",
                "subscription": "sub_test_123",
            }
        },
    }
    resp = await client.post(
        "/api/v1/billing/webhook",
        content=json.dumps(event_payload),
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_billing_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/billing/status")
    assert resp.status_code in (401, 403)
