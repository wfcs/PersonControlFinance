"""Tests for the Accounts API endpoints."""

import pytest
from httpx import AsyncClient

REGISTER_URL = "/api/v1/auth/register"
ACCOUNTS_URL = "/api/v1/accounts"


async def _get_auth_headers(client: AsyncClient, email: str = "acct@test.com") -> dict:
    """Register a user and return auth headers."""
    resp = await client.post(
        REGISTER_URL,
        json={
            "email": email,
            "password": "Str0ngP@ss!",
            "full_name": "Test User",
            "tenant_name": "Test Corp",
        },
    )
    assert resp.status_code == 201
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_account(client: AsyncClient):
    headers = await _get_auth_headers(client)
    resp = await client.post(
        ACCOUNTS_URL,
        json={
            "name": "My Checking",
            "type": "checking",
            "institution": "Bank of Test",
            "balance": "1000.00",
            "currency": "BRL",
        },
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "My Checking"
    assert data["type"] == "checking"
    assert data["institution"] == "Bank of Test"
    assert data["balance"] == "1000.00"
    assert "id" in data
    assert "tenant_id" in data


@pytest.mark.asyncio
async def test_list_accounts(client: AsyncClient):
    headers = await _get_auth_headers(client)
    await client.post(
        ACCOUNTS_URL,
        json={"name": "Checking", "type": "checking"},
        headers=headers,
    )
    await client.post(
        ACCOUNTS_URL,
        json={"name": "Savings", "type": "savings"},
        headers=headers,
    )
    resp = await client.get(ACCOUNTS_URL, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
