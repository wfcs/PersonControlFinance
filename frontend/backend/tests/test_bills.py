"""Testes para API de faturas de cartão de crédito."""

from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient


@pytest.fixture
async def credit_card_account(auth_client: dict) -> dict:
    """Cria uma conta de cartão de crédito."""
    client: AsyncClient = auth_client["client"]
    res = await client.post("/api/v1/accounts/", json={
        "name": "Nubank Crédito",
        "institution_name": "Nubank",
        "type": "credit_card",
        "balance": "-2500.00",
        "credit_limit": "8000.00",
    })
    assert res.status_code == 201
    return res.json()


@pytest.mark.asyncio
async def test_get_bills_empty(auth_client: dict, credit_card_account: dict):
    client: AsyncClient = auth_client["client"]
    account_id = credit_card_account["id"]
    res = await client.get(f"/api/v1/bills/{account_id}")
    assert res.status_code == 200
    assert res.json() == []


@pytest.mark.asyncio
async def test_get_bills_with_transactions(auth_client: dict, credit_card_account: dict):
    client: AsyncClient = auth_client["client"]
    account_id = credit_card_account["id"]
    now = datetime.now(timezone.utc)

    # Criar transações em diferentes datas
    for i in range(5):
        await client.post("/api/v1/transactions/", json={
            "account_id": account_id,
            "description": f"Compra {i + 1}",
            "amount": f"-{100 + i * 50}.00",
            "type": "debit",
            "date": (now - timedelta(days=i * 5)).isoformat(),
        })

    res = await client.get(f"/api/v1/bills/{account_id}?closing_day=25")
    assert res.status_code == 200
    bills = res.json()
    assert len(bills) >= 1
    assert "period" in bills[0]
    assert "total" in bills[0]
    assert "transaction_count" in bills[0]


@pytest.mark.asyncio
async def test_get_bills_not_credit_card(auth_client: dict, sample_account: dict):
    """Conta que não é cartão retorna 404."""
    client: AsyncClient = auth_client["client"]
    res = await client.get(f"/api/v1/bills/{sample_account['id']}")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_get_bills_custom_closing_day(auth_client: dict, credit_card_account: dict):
    client: AsyncClient = auth_client["client"]
    account_id = credit_card_account["id"]
    now = datetime.now(timezone.utc)

    await client.post("/api/v1/transactions/", json={
        "account_id": account_id,
        "description": "Teste Closing Day",
        "amount": "-200.00",
        "type": "debit",
        "date": now.isoformat(),
    })

    res = await client.get(f"/api/v1/bills/{account_id}?closing_day=15")
    assert res.status_code == 200
    assert len(res.json()) >= 1
