from datetime import datetime, timezone

import pytest
from httpx import AsyncClient


def _tx_payload(account_id: str, amount: str = "-150.00", description: str = "Mercado") -> dict:
    return {
        "account_id": account_id,
        "description": description,
        "amount": amount,
        "type": "debit",
        "date": datetime.now(timezone.utc).isoformat(),
    }


@pytest.mark.asyncio
async def test_create_transaction(auth_client: dict, sample_account: dict):
    client: AsyncClient = auth_client["client"]
    res = await client.post("/api/v1/transactions/", json=_tx_payload(sample_account["id"]))
    assert res.status_code == 201
    data = res.json()
    assert data["description"] == "Mercado"
    assert float(data["amount"]) == -150.00


@pytest.mark.asyncio
async def test_list_transactions(auth_client: dict, sample_account: dict):
    client: AsyncClient = auth_client["client"]
    # Cria 3 transações
    for i in range(3):
        await client.post("/api/v1/transactions/", json=_tx_payload(
            sample_account["id"], description=f"Compra {i}"
        ))

    res = await client.get("/api/v1/transactions/")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_list_transactions_filter_by_type(auth_client: dict, sample_account: dict):
    client: AsyncClient = auth_client["client"]
    await client.post("/api/v1/transactions/", json=_tx_payload(sample_account["id"], amount="-50.00"))
    await client.post("/api/v1/transactions/", json={
        **_tx_payload(sample_account["id"], amount="5000.00"),
        "type": "credit",
        "description": "Salário",
    })

    res = await client.get("/api/v1/transactions/?type=credit")
    assert res.status_code == 200
    assert res.json()["total"] == 1
    assert res.json()["items"][0]["description"] == "Salário"


@pytest.mark.asyncio
async def test_list_transactions_search(auth_client: dict, sample_account: dict):
    client: AsyncClient = auth_client["client"]
    await client.post("/api/v1/transactions/", json=_tx_payload(
        sample_account["id"], description="PIX para João"
    ))
    await client.post("/api/v1/transactions/", json=_tx_payload(
        sample_account["id"], description="Supermercado Extra"
    ))

    res = await client.get("/api/v1/transactions/?search=PIX")
    assert res.status_code == 200
    assert res.json()["total"] == 1


@pytest.mark.asyncio
async def test_update_transaction(auth_client: dict, sample_account: dict):
    client: AsyncClient = auth_client["client"]
    create_res = await client.post("/api/v1/transactions/", json=_tx_payload(sample_account["id"]))
    tx_id = create_res.json()["id"]

    res = await client.patch(f"/api/v1/transactions/{tx_id}", json={"notes": "Compra do mês"})
    assert res.status_code == 200
    assert res.json()["notes"] == "Compra do mês"


@pytest.mark.asyncio
async def test_delete_transaction(auth_client: dict, sample_account: dict):
    client: AsyncClient = auth_client["client"]
    create_res = await client.post("/api/v1/transactions/", json=_tx_payload(sample_account["id"]))
    tx_id = create_res.json()["id"]

    res = await client.delete(f"/api/v1/transactions/{tx_id}")
    assert res.status_code == 204

    res_get = await client.get(f"/api/v1/transactions/{tx_id}")
    assert res_get.status_code == 404


@pytest.mark.asyncio
async def test_export_csv(auth_client: dict, sample_account: dict):
    client: AsyncClient = auth_client["client"]
    await client.post("/api/v1/transactions/", json=_tx_payload(sample_account["id"]))

    res = await client.get("/api/v1/transactions/export/csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "Mercado" in res.text


@pytest.mark.asyncio
async def test_monthly_summary(auth_client: dict, sample_account: dict):
    client: AsyncClient = auth_client["client"]
    now = datetime.now(timezone.utc)

    # Receita
    await client.post("/api/v1/transactions/", json={
        **_tx_payload(sample_account["id"], amount="5000.00"),
        "type": "credit",
        "description": "Salário",
    })
    # Despesa
    await client.post("/api/v1/transactions/", json=_tx_payload(
        sample_account["id"], amount="-500.00"
    ))

    res = await client.get(f"/api/v1/transactions/summary?year={now.year}&month={now.month}")
    assert res.status_code == 200
    data = res.json()
    assert float(data["receita"]) == 5000.00
    assert float(data["gasto"]) == 500.00
    assert float(data["resultado"]) == 4500.00


@pytest.mark.asyncio
async def test_transaction_tenant_isolation(client: AsyncClient):
    """Transações de um tenant não devem aparecer para outro."""
    # Registra dois tenants
    for email in ["a@visor.app", "b@visor.app"]:
        await client.post("/api/v1/auth/register", json={"email": email, "password": "Senha@123"})

    async def login(email: str) -> str:
        res = await client.post("/api/v1/auth/login", json={"email": email, "password": "Senha@123"})
        return res.json()["access_token"]

    token_a = await login("a@visor.app")
    token_b = await login("b@visor.app")

    # Cria conta e transação para Tenant A
    acc_res = await client.post("/api/v1/accounts/", json={
        "name": "Conta A", "institution_name": "Banco", "type": "checking"
    }, headers={"Authorization": f"Bearer {token_a}"})
    acc_id = acc_res.json()["id"]

    await client.post("/api/v1/transactions/", json=_tx_payload(acc_id), headers={
        "Authorization": f"Bearer {token_a}"
    })

    # Tenant B não deve ver as transações de A
    res_b = await client.get("/api/v1/transactions/", headers={"Authorization": f"Bearer {token_b}"})
    assert res_b.status_code == 200
    assert res_b.json()["total"] == 0
