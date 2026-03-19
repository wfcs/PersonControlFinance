from __future__ import annotations

import pytest
from httpx import AsyncClient


async def _setup(client: AsyncClient) -> tuple[str, str]:
    """Register, login, create account, return (token, account_id)."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "cf@example.com",
            "full_name": "CF User",
            "password": "strongpass123",
            "tenant_name": "CF Corp",
        },
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "cf@example.com", "password": "strongpass123"},
    )
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post(
        "/api/v1/accounts",
        json={"name": "Main", "type": "checking", "balance": "10000.00"},
        headers=headers,
    )
    account_id = resp.json()["id"]
    return token, account_id


@pytest.mark.asyncio
async def test_cashflow_empty(client: AsyncClient) -> None:
    token, _ = await _setup(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get("/api/v1/cashflow?months=3", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "periods" in data
    assert data["total_income"] == "0"
    assert data["total_expense"] == "0"


@pytest.mark.asyncio
async def test_cashflow_with_transactions(client: AsyncClient) -> None:
    token, account_id = await _setup(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Add income
    await client.post(
        "/api/v1/transactions",
        json={
            "description": "Salary",
            "amount": "5000.00",
            "type": "income",
            "date": "2026-03-01",
            "account_id": account_id,
        },
        headers=headers,
    )
    # Add expense
    await client.post(
        "/api/v1/transactions",
        json={
            "description": "Rent",
            "amount": "2000.00",
            "type": "expense",
            "date": "2026-03-05",
            "account_id": account_id,
        },
        headers=headers,
    )

    resp = await client.get("/api/v1/cashflow?months=3", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["periods"]) >= 1


@pytest.mark.asyncio
async def test_cashflow_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/cashflow")
    assert resp.status_code in (401, 403)
