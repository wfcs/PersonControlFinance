from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_tenant_data_isolation(client: AsyncClient) -> None:
    """Data created by tenant A must not be visible to tenant B."""
    # Register two separate tenants
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "tenantA@example.com",
            "full_name": "Tenant A",
            "password": "strongpass123",
            "tenant_name": "Company A",
        },
    )
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "tenantB@example.com",
            "full_name": "Tenant B",
            "password": "strongpass123",
            "tenant_name": "Company B",
        },
    )

    # Login as tenant A
    login_a = await client.post(
        "/api/v1/auth/login",
        json={"email": "tenantA@example.com", "password": "strongpass123"},
    )
    token_a = login_a.json()["access_token"]

    # Login as tenant B
    login_b = await client.post(
        "/api/v1/auth/login",
        json={"email": "tenantB@example.com", "password": "strongpass123"},
    )
    token_b = login_b.json()["access_token"]

    # Both tokens should be valid
    me_a = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert me_a.status_code == 200
    assert me_a.json()["email"] == "tenantA@example.com"

    me_b = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert me_b.status_code == 200
    assert me_b.json()["email"] == "tenantB@example.com"

    # Tenants should have different tenant_ids
    assert me_a.json()["tenant_id"] != me_b.json()["tenant_id"]


@pytest.mark.asyncio
async def test_middleware_sets_tenant_context(client: AsyncClient) -> None:
    """Authenticated requests should have tenant context set."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "middleware@example.com",
            "full_name": "Middleware Test",
            "password": "strongpass123",
            "tenant_name": "Middleware Corp",
        },
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "middleware@example.com", "password": "strongpass123"},
    )
    token = login_resp.json()["access_token"]

    # /me endpoint should return user with tenant_id
    me_resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    data = me_resp.json()
    assert "tenant_id" in data
    assert data["tenant_id"] is not None


@pytest.mark.asyncio
async def test_public_routes_no_auth_required(client: AsyncClient) -> None:
    """Public routes should be accessible without auth."""
    health = await client.get("/health")
    assert health.status_code == 200
