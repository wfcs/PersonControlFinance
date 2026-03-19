from __future__ import annotations

import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "acct@example.com",
            "full_name": "Acct User",
            "password": "strongpass123",
            "tenant_name": "Acct Corp",
        },
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "acct@example.com", "password": "strongpass123"},
    )
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_create_account(client: AsyncClient) -> None:
    token = await _register_and_login(client)
    resp = await client.post(
        "/api/v1/accounts",
        json={"name": "Nubank", "type": "checking", "balance": "1500.00"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Nubank"
    assert data["type"] == "checking"
    assert data["balance"] == "1500.00"


@pytest.mark.asyncio
async def test_list_accounts(client: AsyncClient) -> None:
    token = await _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    await client.post(
        "/api/v1/accounts",
        json={"name": "Itaú", "type": "checking"},
        headers=headers,
    )
    resp = await client.get("/api/v1/accounts", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_update_account(client: AsyncClient) -> None:
    token = await _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    create_resp = await client.post(
        "/api/v1/accounts",
        json={"name": "Old Name", "type": "savings"},
        headers=headers,
    )
    account_id = create_resp.json()["id"]
    resp = await client.patch(
        f"/api/v1/accounts/{account_id}",
        json={"name": "New Name"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_account(client: AsyncClient) -> None:
    token = await _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    create_resp = await client.post(
        "/api/v1/accounts",
        json={"name": "To Delete", "type": "checking"},
        headers=headers,
    )
    account_id = create_resp.json()["id"]
    resp = await client.delete(f"/api/v1/accounts/{account_id}", headers=headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_accounts_require_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/accounts")
    assert resp.status_code in (401, 403)
