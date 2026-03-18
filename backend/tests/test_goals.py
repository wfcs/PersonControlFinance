"""Tests for the Goals API endpoints."""

import pytest
from httpx import AsyncClient

REGISTER_URL = "/api/v1/auth/register"
GOALS_URL = "/api/v1/goals"


async def _get_auth_headers(client: AsyncClient, email: str = "goal@test.com") -> dict:
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
async def test_create_goal(client: AsyncClient):
    headers = await _get_auth_headers(client)
    resp = await client.post(
        GOALS_URL,
        json={"name": "Emergency Fund", "target_amount": "10000.00"},
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Emergency Fund"
    assert data["target_amount"] == "10000.00"
    assert data["current_amount"] == "0.00"
    assert data["progress"] == 0.0
    assert data["status"] == "in_progress"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_goals(client: AsyncClient):
    headers = await _get_auth_headers(client)
    await client.post(
        GOALS_URL,
        json={"name": "Goal 1", "target_amount": "5000.00"},
        headers=headers,
    )
    await client.post(
        GOALS_URL,
        json={"name": "Goal 2", "target_amount": "3000.00"},
        headers=headers,
    )
    resp = await client.get(GOALS_URL, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_update_goal_progress(client: AsyncClient):
    headers = await _get_auth_headers(client)
    create_resp = await client.post(
        GOALS_URL,
        json={"name": "Vacation", "target_amount": "5000.00"},
        headers=headers,
    )
    goal_id = create_resp.json()["id"]
    resp = await client.put(
        f"{GOALS_URL}/{goal_id}",
        json={"current_amount": "2500.00"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["current_amount"] == "2500.00"
    assert data["progress"] == 50.0
