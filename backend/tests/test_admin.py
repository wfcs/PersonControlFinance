"""Testes dos endpoints de administração."""

import pytest
from httpx import AsyncClient


async def test_admin_stats_requires_admin(client: AsyncClient):
    """GET /admin/stats sem admin retorna 403."""
    res = await client.get("/api/v1/admin/stats")
    assert res.status_code in (401, 403)


async def test_admin_tenants_requires_admin(client: AsyncClient):
    """GET /admin/tenants sem admin retorna 403."""
    res = await client.get("/api/v1/admin/tenants")
    assert res.status_code in (401, 403)


async def test_admin_users_requires_admin(client: AsyncClient):
    """GET /admin/users sem admin retorna 403."""
    res = await client.get("/api/v1/admin/users")
    assert res.status_code in (401, 403)


async def test_admin_stats_with_admin_role(auth_client: dict):
    """Admin autenticado consegue acessar stats."""
    from app.api.v1.admin import ADMIN_EMAILS, _load_admin_emails

    client: AsyncClient = auth_client["client"]

    # Registra o email do test user como admin
    ADMIN_EMAILS.add("dev@visor.app")

    res = await client.get("/api/v1/admin/stats")
    assert res.status_code == 200

    data = res.json()
    assert "total_tenants" in data
    assert "total_users" in data
    assert "tenants_by_plan" in data
    assert data["total_users"] >= 1

    ADMIN_EMAILS.discard("dev@visor.app")


async def test_admin_list_tenants_with_admin_role(auth_client: dict):
    """Admin autenticado consegue listar tenants."""
    from app.api.v1.admin import ADMIN_EMAILS

    client: AsyncClient = auth_client["client"]
    ADMIN_EMAILS.add("dev@visor.app")

    res = await client.get("/api/v1/admin/tenants")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) >= 1

    ADMIN_EMAILS.discard("dev@visor.app")


async def test_admin_list_users_with_admin_role(auth_client: dict):
    """Admin autenticado consegue listar usuários."""
    from app.api.v1.admin import ADMIN_EMAILS

    client: AsyncClient = auth_client["client"]
    ADMIN_EMAILS.add("dev@visor.app")

    res = await client.get("/api/v1/admin/users")
    assert res.status_code == 200

    users = res.json()
    assert isinstance(users, list)
    assert len(users) >= 1
    assert users[0]["email"] == "dev@visor.app"

    ADMIN_EMAILS.discard("dev@visor.app")


async def test_admin_update_tenant_plan(auth_client: dict):
    """Admin pode alterar o plano de um tenant."""
    from app.api.v1.admin import ADMIN_EMAILS

    client: AsyncClient = auth_client["client"]
    ADMIN_EMAILS.add("dev@visor.app")

    # Pega lista de tenants
    res = await client.get("/api/v1/admin/tenants")
    tenants = res.json()
    tenant_id = tenants[0]["id"]

    # Atualiza plano
    res = await client.patch(
        f"/api/v1/admin/tenants/{tenant_id}",
        json={"plan": "pro"},
    )
    assert res.status_code == 200
    assert res.json()["plan"] == "pro"

    ADMIN_EMAILS.discard("dev@visor.app")
