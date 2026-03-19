from __future__ import annotations

import pytest
from httpx import AsyncClient


async def _setup(client: AsyncClient) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "nw@example.com",
            "full_name": "NW User",
            "password": "strongpass123",
            "tenant_name": "NW Corp",
        },
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "nw@example.com", "password": "strongpass123"},
    )
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_networth_empty(client: AsyncClient) -> None:
    token = await _setup(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get("/api/v1/networth", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["current_assets"] == "0"
    assert data["current_liabilities"] == "0"
    assert data["current_net_worth"] == "0"


@pytest.mark.asyncio
async def test_networth_with_accounts(client: AsyncClient) -> None:
    token = await _setup(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Asset
    await client.post(
        "/api/v1/accounts",
        json={"name": "Checking", "type": "checking", "balance": "15000.00"},
        headers=headers,
    )
    # Liability
    await client.post(
        "/api/v1/accounts",
        json={"name": "Credit Card", "type": "credit_card", "balance": "3000.00"},
        headers=headers,
    )

    resp = await client.get("/api/v1/networth", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["current_assets"] == "15000.00"
    assert data["current_liabilities"] == "3000.00"
    assert data["current_net_worth"] == "12000.00"
