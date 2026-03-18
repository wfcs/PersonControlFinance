from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "alice@example.com",
            "full_name": "Alice Smith",
            "password": "strongpass123",
            "tenant_name": "Alice Corp",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert data["full_name"] == "Alice Smith"
    assert "id" in data
    assert "tenant_id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient) -> None:
    payload = {
        "email": "dup@example.com",
        "full_name": "Dup User",
        "password": "strongpass123",
        "tenant_name": "Dup Corp",
    }
    await client.post("/api/v1/auth/register", json=payload)
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login(client: AsyncClient) -> None:
    # Register first
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "bob@example.com",
            "full_name": "Bob Jones",
            "password": "strongpass123",
            "tenant_name": "Bob Inc",
        },
    )
    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "bob@example.com", "password": "strongpass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrong@example.com",
            "full_name": "Wrong Pass",
            "password": "strongpass123",
            "tenant_name": "Wrong Corp",
        },
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "badpassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me(client: AsyncClient) -> None:
    # Register + login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "carol@example.com",
            "full_name": "Carol Davis",
            "password": "strongpass123",
            "tenant_name": "Carol LLC",
        },
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "carol@example.com", "password": "strongpass123"},
    )
    token = login_resp.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "carol@example.com"
    assert data["full_name"] == "Carol Davis"


@pytest.mark.asyncio
async def test_me_unauthorized(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me")
    assert response.status_code in (401, 403)  # HTTPBearer may return either


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient) -> None:
    # Register + login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "dave@example.com",
            "full_name": "Dave Wilson",
            "password": "strongpass123",
            "tenant_name": "Dave Co",
        },
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "dave@example.com", "password": "strongpass123"},
    )
    refresh_token = login_resp.json()["refresh_token"]

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_refresh_with_invalid_token(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid.token.here"},
    )
    assert response.status_code == 401
