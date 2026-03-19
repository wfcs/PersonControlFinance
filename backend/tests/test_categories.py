from __future__ import annotations

import pytest
from httpx import AsyncClient


async def _auth(client: AsyncClient) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "cat@example.com",
            "full_name": "Cat User",
            "password": "strongpass123",
            "tenant_name": "Cat Corp",
        },
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "cat@example.com", "password": "strongpass123"},
    )
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_crud_categories(client: AsyncClient) -> None:
    token = await _auth(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create
    resp = await client.post(
        "/api/v1/categories",
        json={"name": "Food", "type": "expense", "color": "#FF5733"},
        headers=headers,
    )
    assert resp.status_code == 201
    cat_id = resp.json()["id"]
    assert resp.json()["name"] == "Food"

    # List
    resp = await client.get("/api/v1/categories", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

    # Update
    resp = await client.patch(
        f"/api/v1/categories/{cat_id}",
        json={"name": "Alimentação"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Alimentação"

    # Delete
    resp = await client.delete(f"/api/v1/categories/{cat_id}", headers=headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_subcategory(client: AsyncClient) -> None:
    token = await _auth(client)
    headers = {"Authorization": f"Bearer {token}"}

    parent = await client.post(
        "/api/v1/categories",
        json={"name": "Transport", "type": "expense"},
        headers=headers,
    )
    parent_id = parent.json()["id"]

    child = await client.post(
        "/api/v1/categories",
        json={"name": "Uber", "type": "expense", "parent_id": parent_id},
        headers=headers,
    )
    assert child.status_code == 201
    assert child.json()["parent_id"] == parent_id
