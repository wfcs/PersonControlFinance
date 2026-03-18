"""Tests for the authentication endpoints."""

import pytest
from httpx import AsyncClient

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
REFRESH_URL = "/api/v1/auth/refresh"
LOGOUT_URL = "/api/v1/auth/logout"

REGISTER_PAYLOAD = {
    "email": "alice@example.com",
    "password": "Str0ngP@ss!",
    "full_name": "Alice Test",
    "tenant_name": "Alice Corp",
}


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    response = await client.post(REGISTER_URL, json=REGISTER_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    await client.post(REGISTER_URL, json=REGISTER_PAYLOAD)
    response = await client.post(REGISTER_URL, json=REGISTER_PAYLOAD)
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post(REGISTER_URL, json=REGISTER_PAYLOAD)
    response = await client.post(
        LOGIN_URL,
        json={"email": "alice@example.com", "password": "Str0ngP@ss!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post(REGISTER_URL, json=REGISTER_PAYLOAD)
    response = await client.post(
        LOGIN_URL,
        json={"email": "alice@example.com", "password": "wrong"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_success(client: AsyncClient):
    reg = await client.post(REGISTER_URL, json=REGISTER_PAYLOAD)
    refresh_token = reg.json()["refresh_token"]
    response = await client.post(
        REFRESH_URL,
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient):
    response = await client.post(
        REFRESH_URL,
        json={"refresh_token": "invalid.token.here"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    response = await client.post(LOGOUT_URL)
    assert response.status_code == 200
    assert response.json()["detail"] == "Successfully logged out"
