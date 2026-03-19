from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.notification_service import create_notification
from app.schemas.notification import NotificationCreate


async def _register_and_login(client: AsyncClient) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "notif@example.com",
            "full_name": "Notif User",
            "password": "strongpass123",
            "tenant_name": "Notif Corp",
        },
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "notif@example.com", "password": "strongpass123"},
    )
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_notifications_empty(client: AsyncClient) -> None:
    token = await _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get("/api/v1/notifications", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_notifications_crud(client: AsyncClient, db_session: AsyncSession) -> None:
    token = await _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Get user info
    me = await client.get("/api/v1/auth/me", headers=headers)
    user_id = me.json()["id"]
    tenant_id = me.json()["tenant_id"]

    from uuid import UUID
    await create_notification(
        user_id=UUID(user_id),
        tenant_id=UUID(tenant_id),
        data=NotificationCreate(title="Test", message="Hello"),
        session=db_session,
    )
    await db_session.commit()

    # List
    resp = await client.get("/api/v1/notifications", headers=headers)
    assert resp.status_code == 200
    notifs = resp.json()
    assert len(notifs) >= 1
    notif_id = notifs[0]["id"]
    assert notifs[0]["is_read"] is False

    # Mark as read
    resp = await client.patch(
        f"/api/v1/notifications/{notif_id}/read", headers=headers
    )
    assert resp.status_code == 204

    # Mark all as read
    resp = await client.post("/api/v1/notifications/read-all", headers=headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_notifications_require_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/notifications")
    assert resp.status_code in (401, 403)
