"""Tests for the Categories API endpoints."""

import pytest
from httpx import AsyncClient

REGISTER_URL = "/api/v1/auth/register"
CATEGORIES_URL = "/api/v1/categories"


async def _get_auth_headers(client: AsyncClient, email: str = "cat@test.com") -> dict:
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
async def test_create_category(client: AsyncClient):
    headers = await _get_auth_headers(client)
    resp = await client.post(
        CATEGORIES_URL,
        json={"name": "Alimentacao", "type": "expense", "color": "#FF0000"},
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Alimentacao"
    assert data["type"] == "expense"
    assert data["color"] == "#FF0000"
    assert "id" in data
    assert "tenant_id" in data


@pytest.mark.asyncio
async def test_list_categories(client: AsyncClient):
    headers = await _get_auth_headers(client)
    # Create two categories
    await client.post(
        CATEGORIES_URL,
        json={"name": "Transporte", "type": "expense"},
        headers=headers,
    )
    await client.post(
        CATEGORIES_URL,
        json={"name": "Salario", "type": "income"},
        headers=headers,
    )
    resp = await client.get(CATEGORIES_URL, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_update_category(client: AsyncClient):
    headers = await _get_auth_headers(client)
    create_resp = await client.post(
        CATEGORIES_URL,
        json={"name": "Old Name", "type": "expense"},
        headers=headers,
    )
    cat_id = create_resp.json()["id"]
    resp = await client.put(
        f"{CATEGORIES_URL}/{cat_id}",
        json={"name": "New Name"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_category(client: AsyncClient):
    headers = await _get_auth_headers(client)
    create_resp = await client.post(
        CATEGORIES_URL,
        json={"name": "ToDelete", "type": "expense"},
        headers=headers,
    )
    cat_id = create_resp.json()["id"]
    resp = await client.delete(f"{CATEGORIES_URL}/{cat_id}", headers=headers)
    assert resp.status_code == 200
    # Verify it's gone
    get_resp = await client.get(f"{CATEGORIES_URL}/{cat_id}", headers=headers)
    assert get_resp.status_code == 404
