import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_account(auth_client: dict):
    client: AsyncClient = auth_client["client"]
    res = await client.post("/api/v1/accounts/", json={
        "name": "Itaú Corrente",
        "institution_name": "Itaú",
        "type": "checking",
        "balance": "2500.00",
    })
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Itaú Corrente"
    assert data["type"] == "checking"
    assert float(data["balance"]) == 2500.00


@pytest.mark.asyncio
async def test_list_accounts(auth_client: dict, sample_account: dict):
    client: AsyncClient = auth_client["client"]
    res = await client.get("/api/v1/accounts/")
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 1
    assert items[0]["id"] == sample_account["id"]


@pytest.mark.asyncio
async def test_get_account(auth_client: dict, sample_account: dict):
    client: AsyncClient = auth_client["client"]
    account_id = sample_account["id"]
    res = await client.get(f"/api/v1/accounts/{account_id}")
    assert res.status_code == 200
    assert res.json()["id"] == account_id


@pytest.mark.asyncio
async def test_update_account(auth_client: dict, sample_account: dict):
    client: AsyncClient = auth_client["client"]
    account_id = sample_account["id"]
    res = await client.patch(f"/api/v1/accounts/{account_id}", json={"name": "Nubank Gold"})
    assert res.status_code == 200
    assert res.json()["name"] == "Nubank Gold"


@pytest.mark.asyncio
async def test_delete_account(auth_client: dict, sample_account: dict):
    client: AsyncClient = auth_client["client"]
    account_id = sample_account["id"]
    res = await client.delete(f"/api/v1/accounts/{account_id}")
    assert res.status_code == 204

    # Não deve aparecer na listagem (soft delete)
    res = await client.get("/api/v1/accounts/")
    assert res.status_code == 200
    assert all(a["id"] != account_id for a in res.json())


@pytest.mark.asyncio
async def test_account_isolation(client: AsyncClient):
    """Garante que usuários de tenants diferentes não veem contas alheias."""
    # Tenant A
    await client.post("/api/v1/auth/register", json={
        "email": "tenantA@fincontrol.app", "password": "Senha@123"
    })
    res_a = await client.post("/api/v1/auth/login", json={
        "email": "tenantA@fincontrol.app", "password": "Senha@123"
    })
    token_a = res_a.json()["access_token"]

    await client.post("/api/v1/accounts/", json={
        "name": "Conta A", "institution_name": "BancoA", "type": "checking"
    }, headers={"Authorization": f"Bearer {token_a}"})

    # Tenant B
    await client.post("/api/v1/auth/register", json={
        "email": "tenantB@fincontrol.app", "password": "Senha@123"
    })
    res_b = await client.post("/api/v1/auth/login", json={
        "email": "tenantB@fincontrol.app", "password": "Senha@123"
    })
    token_b = res_b.json()["access_token"]

    contas_b = await client.get("/api/v1/accounts/", headers={"Authorization": f"Bearer {token_b}"})
    assert contas_b.status_code == 200
    # Tenant B não deve ver a conta do Tenant A
    assert all(a["name"] != "Conta A" for a in contas_b.json())
