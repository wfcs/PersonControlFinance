"""Tests for the Transactions API endpoints."""

import pytest
from httpx import AsyncClient

REGISTER_URL = "/api/v1/auth/register"
ACCOUNTS_URL = "/api/v1/accounts"
CATEGORIES_URL = "/api/v1/categories"
TRANSACTIONS_URL = "/api/v1/transactions"


async def _get_auth_headers(client: AsyncClient, email: str = "tx@test.com") -> dict:
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


async def _create_account(client: AsyncClient, headers: dict) -> str:
    """Create a test account and return its ID."""
    resp = await client.post(
        ACCOUNTS_URL,
        json={"name": "Checking", "type": "checking", "institution": "TestBank"},
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _create_category(client: AsyncClient, headers: dict) -> str:
    """Create a test category and return its ID."""
    resp = await client.post(
        CATEGORIES_URL,
        json={"name": "Alimentacao", "type": "expense"},
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_create_transaction(client: AsyncClient):
    headers = await _get_auth_headers(client)
    account_id = await _create_account(client, headers)
    category_id = await _create_category(client, headers)

    resp = await client.post(
        TRANSACTIONS_URL,
        json={
            "description": "Grocery Shopping",
            "amount": "150.50",
            "type": "expense",
            "date": "2025-01-15",
            "account_id": account_id,
            "category_id": category_id,
        },
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["description"] == "Grocery Shopping"
    assert data["amount"] == "150.50"
    assert data["type"] == "expense"
    assert data["account_id"] == account_id
    assert data["category_id"] == category_id


@pytest.mark.asyncio
async def test_list_transactions_with_filters(client: AsyncClient):
    headers = await _get_auth_headers(client)
    account_id = await _create_account(client, headers)

    # Create multiple transactions
    for i in range(3):
        await client.post(
            TRANSACTIONS_URL,
            json={
                "description": f"Transaction {i}",
                "amount": f"{(i + 1) * 100}.00",
                "type": "expense",
                "date": f"2025-01-{15 + i:02d}",
                "account_id": account_id,
            },
            headers=headers,
        )

    # List all
    resp = await client.get(TRANSACTIONS_URL, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3

    # Filter by type
    resp = await client.get(
        TRANSACTIONS_URL, params={"type": "expense"}, headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["total"] == 3

    # Filter by date range
    resp = await client.get(
        TRANSACTIONS_URL,
        params={"start_date": "2025-01-16", "end_date": "2025-01-17"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["total"] == 2


@pytest.mark.asyncio
async def test_list_transactions_pagination(client: AsyncClient):
    headers = await _get_auth_headers(client)
    account_id = await _create_account(client, headers)

    # Create 5 transactions
    for i in range(5):
        await client.post(
            TRANSACTIONS_URL,
            json={
                "description": f"TX {i}",
                "amount": "50.00",
                "type": "expense",
                "date": "2025-01-15",
                "account_id": account_id,
            },
            headers=headers,
        )

    # Page 1, size 2
    resp = await client.get(
        TRANSACTIONS_URL, params={"page": 1, "page_size": 2}, headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2

    # Page 3, size 2 (should have 1 item)
    resp = await client.get(
        TRANSACTIONS_URL, params={"page": 3, "page_size": 2}, headers=headers
    )
    data = resp.json()
    assert len(data["items"]) == 1
