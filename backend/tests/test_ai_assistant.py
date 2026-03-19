from __future__ import annotations

import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "ai@example.com",
            "full_name": "AI User",
            "password": "strongpass123",
            "tenant_name": "AI Corp",
        },
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "ai@example.com", "password": "strongpass123"},
    )
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_ai_requires_premium(client: AsyncClient) -> None:
    """Free plan users should get 403."""
    token = await _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.post(
        "/api/v1/ai/ask",
        json={"question": "Qual meu saldo?"},
        headers=headers,
    )
    assert resp.status_code == 403
    assert "Premium" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_ai_requires_auth(client: AsyncClient) -> None:
    resp = await client.post("/api/v1/ai/ask", json={"question": "test"})
    assert resp.status_code in (401, 403)
