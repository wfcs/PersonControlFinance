from __future__ import annotations

import pytest
from httpx import AsyncClient


async def _setup(client: AsyncClient) -> tuple[str, str]:
    """Register, login, create an account. Returns (token, account_id)."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "txn@example.com",
            "full_name": "Txn User",
            "password": "strongpass123",
            "tenant_name": "Txn Corp",
        },
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "txn@example.com", "password": "strongpass123"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    acct = await client.post(
        "/api/v1/accounts",
        json={"name": "Main", "type": "checking"},
        headers=headers,
    )
    return token, acct.json()["id"]


@pytest.mark.asyncio
async def test_create_transaction(client: AsyncClient) -> None:
    token, account_id = await _setup(client)
    resp = await client.post(
        "/api/v1/transactions",
        json={
            "description": "Salary",
            "amount": "5000.00",
            "type": "income",
            "date": "2026-03-01",
            "account_id": account_id,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["description"] == "Salary"
    assert data["amount"] == "5000.00"
    assert data["type"] == "income"


@pytest.mark.asyncio
async def test_list_transactions_with_filters(client: AsyncClient) -> None:
    token, account_id = await _setup(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create two transactions
    await client.post(
        "/api/v1/transactions",
        json={
            "description": "Grocery",
            "amount": "150.00",
            "type": "expense",
            "date": "2026-03-10",
            "account_id": account_id,
        },
        headers=headers,
    )
    await client.post(
        "/api/v1/transactions",
        json={
            "description": "Freelance",
            "amount": "2000.00",
            "type": "income",
            "date": "2026-03-15",
            "account_id": account_id,
        },
        headers=headers,
    )

    # List all
    resp = await client.get("/api/v1/transactions", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2

    # Filter by type
    resp = await client.get("/api/v1/transactions?type=income", headers=headers)
    assert len(resp.json()) == 1
    assert resp.json()[0]["description"] == "Freelance"

    # Filter by search
    resp = await client.get("/api/v1/transactions?search=Groc", headers=headers)
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_update_transaction(client: AsyncClient) -> None:
    token, account_id = await _setup(client)
    headers = {"Authorization": f"Bearer {token}"}
    create_resp = await client.post(
        "/api/v1/transactions",
        json={
            "description": "Old",
            "amount": "100.00",
            "type": "expense",
            "date": "2026-03-01",
            "account_id": account_id,
        },
        headers=headers,
    )
    txn_id = create_resp.json()["id"]
    resp = await client.patch(
        f"/api/v1/transactions/{txn_id}",
        json={"description": "Updated"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["description"] == "Updated"


@pytest.mark.asyncio
async def test_delete_transaction(client: AsyncClient) -> None:
    token, account_id = await _setup(client)
    headers = {"Authorization": f"Bearer {token}"}
    create_resp = await client.post(
        "/api/v1/transactions",
        json={
            "description": "To Delete",
            "amount": "50.00",
            "type": "expense",
            "date": "2026-03-01",
            "account_id": account_id,
        },
        headers=headers,
    )
    txn_id = create_resp.json()["id"]
    resp = await client.delete(f"/api/v1/transactions/{txn_id}", headers=headers)
    assert resp.status_code == 204
