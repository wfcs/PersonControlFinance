from __future__ import annotations

import pytest
from httpx import AsyncClient


async def _auth(client: AsyncClient) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "goal@example.com",
            "full_name": "Goal User",
            "password": "strongpass123",
            "tenant_name": "Goal Corp",
        },
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "goal@example.com", "password": "strongpass123"},
    )
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_crud_goals(client: AsyncClient) -> None:
    token = await _auth(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create
    resp = await client.post(
        "/api/v1/goals",
        json={
            "name": "Emergency Fund",
            "target_amount": "10000.00",
            "deadline": "2026-12-31",
        },
        headers=headers,
    )
    assert resp.status_code == 201
    goal_id = resp.json()["id"]
    assert resp.json()["name"] == "Emergency Fund"
    assert resp.json()["status"] == "active"

    # List
    resp = await client.get("/api/v1/goals", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

    # Update progress
    resp = await client.patch(
        f"/api/v1/goals/{goal_id}",
        json={"current_amount": "2500.00"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["current_amount"] == "2500.00"

    # Delete
    resp = await client.delete(f"/api/v1/goals/{goal_id}", headers=headers)
    assert resp.status_code == 204
