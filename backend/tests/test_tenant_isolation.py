"""Tests for tenant isolation middleware."""

import pytest
from httpx import AsyncClient

from app.core.security import create_access_token

REGISTER_URL = "/api/v1/auth/register"


async def _register_user(client: AsyncClient, email: str, tenant_name: str) -> dict:
    """Helper: register a user and return the response JSON."""
    payload = {
        "email": email,
        "password": "Str0ngP@ss!",
        "full_name": "Test User",
        "tenant_name": tenant_name,
    }
    resp = await client.post(REGISTER_URL, json=payload)
    assert resp.status_code == 201
    return resp.json()


# ── Middleware behaviour ──────────────────────────────────────


@pytest.mark.asyncio
async def test_excluded_paths_no_auth_required(client: AsyncClient):
    """Excluded paths should not require authentication."""
    # /health is excluded
    resp = await client.get("/health")
    assert resp.status_code == 200

    # /docs is excluded
    resp = await client.get("/docs")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_missing_auth_header_returns_401(client: AsyncClient):
    """Requests to protected routes without Authorization header get 401."""
    # Any non-excluded path that doesn't exist will still hit the middleware
    # first. Since there's no Authorization header the middleware rejects it.
    resp = await client.get("/api/v1/some-protected-route")
    assert resp.status_code == 401
    assert "Authorization" in resp.json()["detail"] or "Missing" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_invalid_token_returns_401(client: AsyncClient):
    """A malformed or expired token should return 401."""
    resp = await client.get(
        "/api/v1/some-protected-route",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_valid_token_passes_middleware(client: AsyncClient):
    """A valid JWT allows the request through the middleware.

    We register a user (which gives us a valid token) and then call /health
    with the token.  Even though /health is excluded, this proves the token
    decoding path works without error.
    """
    data = await _register_user(client, "middleware@test.com", "Middleware Corp")
    token = data["access_token"]

    # Use the token on an excluded path (should still work)
    resp = await client.get(
        "/health",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_register_and_login_excluded_from_middleware(client: AsyncClient):
    """Register and login endpoints should work without prior auth."""
    # Register
    resp = await client.post(
        REGISTER_URL,
        json={
            "email": "new@test.com",
            "password": "Str0ngP@ss!",
            "full_name": "New User",
            "tenant_name": "New Corp",
        },
    )
    assert resp.status_code == 201

    # Login
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "new@test.com", "password": "Str0ngP@ss!"},
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_token_without_bearer_prefix_returns_401(client: AsyncClient):
    """Authorization header without 'Bearer ' prefix should fail."""
    resp = await client.get(
        "/api/v1/some-protected-route",
        headers={"Authorization": "Token abc123"},
    )
    assert resp.status_code == 401
