from __future__ import annotations

import pytest
from httpx import AsyncClient


async def _setup(client: AsyncClient) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "proj@example.com",
            "full_name": "Proj User",
            "password": "strongpass123",
            "tenant_name": "Proj Corp",
        },
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "proj@example.com", "password": "strongpass123"},
    )
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_projection_empty(client: AsyncClient) -> None:
    token = await _setup(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get("/api/v1/projection?months=3", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "current_balance" in data
    assert "points" in data
    assert data["current_balance"] in ("0", "0.00")


@pytest.mark.asyncio
async def test_projection_with_balance(client: AsyncClient) -> None:
    token = await _setup(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create account with balance
    await client.post(
        "/api/v1/accounts",
        json={"name": "Savings", "type": "savings", "balance": "10000.00"},
        headers=headers,
    )

    resp = await client.get("/api/v1/projection?months=6", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["current_balance"] == "10000.00"
    assert len(data["points"]) >= 1
