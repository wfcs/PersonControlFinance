from __future__ import annotations

import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "admin@example.com",
            "full_name": "Admin User",
            "password": "strongpass123",
            "tenant_name": "Admin Corp",
        },
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "strongpass123"},
    )
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_admin_stats_forbidden(client: AsyncClient) -> None:
    """Non-admin users should get 403."""
    token = await _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get("/api/v1/admin/stats", headers=headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_tenants_forbidden(client: AsyncClient) -> None:
    token = await _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get("/api/v1/admin/tenants", headers=headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/admin/stats")
    assert resp.status_code in (401, 403)
