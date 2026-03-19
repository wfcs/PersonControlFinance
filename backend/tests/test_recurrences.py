from __future__ import annotations

import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "rec@example.com",
            "full_name": "Rec User",
            "password": "strongpass123",
            "tenant_name": "Rec Corp",
        },
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "rec@example.com", "password": "strongpass123"},
    )
    return resp.json()["access_token"]


async def _create_account(client: AsyncClient, token: str) -> str:
    resp = await client.post(
        "/api/v1/accounts",
        json={"name": "Main Account", "type": "checking", "balance": "5000.00"},
        headers={"Authorization": f"Bearer {token}"},
    )
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_recurrence_crud(client: AsyncClient) -> None:
    token = await _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    account_id = await _create_account(client, token)

    # Create
    resp = await client.post(
        "/api/v1/recurrences",
        json={
            "description": "Netflix",
            "amount": "39.90",
            "type": "expense",
            "frequency": "mensal",
            "next_due_date": "2026-04-01",
            "account_id": account_id,
        },
        headers=headers,
    )
    assert resp.status_code == 201
    rec_id = resp.json()["id"]
    assert resp.json()["description"] == "Netflix"

    # List
    resp = await client.get("/api/v1/recurrences", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

    # Update
    resp = await client.patch(
        f"/api/v1/recurrences/{rec_id}",
        json={"amount": "44.90"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["amount"] == "44.90"

    # Delete
    resp = await client.delete(f"/api/v1/recurrences/{rec_id}", headers=headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_process_due_recurrences(client: AsyncClient) -> None:
    token = await _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    account_id = await _create_account(client, token)

    # Create a recurrence due today
    await client.post(
        "/api/v1/recurrences",
        json={
            "description": "Rent",
            "amount": "2000.00",
            "type": "expense",
            "frequency": "mensal",
            "next_due_date": "2020-01-01",  # Already past due
            "account_id": account_id,
        },
        headers=headers,
    )

    # Process due
    resp = await client.post("/api/v1/recurrences/process", headers=headers)
    assert resp.status_code == 200
    txns = resp.json()
    assert len(txns) >= 1
    assert "[Recorrência]" in txns[0]["description"]


@pytest.mark.asyncio
async def test_recurrences_require_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/recurrences")
    assert resp.status_code in (401, 403)
