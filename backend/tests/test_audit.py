from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.services.audit_service import log_action


async def _register_and_login(client: AsyncClient) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "audit@example.com",
            "full_name": "Audit User",
            "password": "strongpass123",
            "tenant_name": "Audit Corp",
        },
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "audit@example.com", "password": "strongpass123"},
    )
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_audit_log_empty(client: AsyncClient) -> None:
    token = await _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get("/api/v1/audit", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_audit_log_records_action(client: AsyncClient, db_session: AsyncSession) -> None:
    token = await _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create an account (which we can audit)
    resp = await client.post(
        "/api/v1/accounts",
        json={"name": "Test Account", "type": "checking"},
        headers=headers,
    )
    account_id = resp.json()["id"]

    # Manually log an audit entry
    me = await client.get("/api/v1/auth/me", headers=headers)
    tenant_id = me.json()["tenant_id"]

    from uuid import UUID
    await log_action(
        session=db_session,
        tenant_id=UUID(tenant_id),
        action="create",
        entity_type="account",
        entity_id=account_id,
        changes={"name": "Test Account"},
    )
    await db_session.commit()

    # Retrieve audit logs
    resp = await client.get("/api/v1/audit?entity_type=account", headers=headers)
    assert resp.status_code == 200
    logs = resp.json()
    assert len(logs) >= 1
    assert logs[0]["action"] == "create"
    assert logs[0]["entity_type"] == "account"


@pytest.mark.asyncio
async def test_audit_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/audit")
    assert resp.status_code in (401, 403)
