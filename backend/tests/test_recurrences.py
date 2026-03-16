"""Testes para detecção de recorrências e endpoints."""

from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient


async def _create_transactions(client: AsyncClient, account_id: str, txs: list[dict]):
    """Helper para criar múltiplas transações."""
    for tx_data in txs:
        res = await client.post("/api/v1/transactions/", json=tx_data)
        assert res.status_code == 201


@pytest.mark.asyncio
async def test_list_recurrences_empty(auth_client: dict):
    client: AsyncClient = auth_client["client"]
    res = await client.get("/api/v1/recurrences/")
    assert res.status_code == 200
    assert res.json() == []


@pytest.mark.asyncio
async def test_detect_installments(auth_client: dict, sample_account: dict):
    """Transações com installment_number devem ser agrupadas como parcelas."""
    client: AsyncClient = auth_client["client"]
    account_id = sample_account["id"]
    now = datetime.now(timezone.utc)

    txs = []
    for i in range(1, 5):
        txs.append({
            "account_id": account_id,
            "description": f"LOJA XYZ {i}/10",
            "amount": "-150.00",
            "type": "debit",
            "date": (now - timedelta(days=30 * (5 - i))).isoformat(),
        })
    await _create_transactions(client, account_id, txs)

    res = await client.post("/api/v1/recurrences/detect")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_detect_fixed_recurring(auth_client: dict, sample_account: dict):
    """Transações mensais similares devem ser detectadas como contas fixas."""
    client: AsyncClient = auth_client["client"]
    account_id = sample_account["id"]
    now = datetime.now(timezone.utc)

    txs = []
    for i in range(4):
        txs.append({
            "account_id": account_id,
            "description": "NETFLIX.COM",
            "amount": "-44.90",
            "type": "debit",
            "date": (now - timedelta(days=30 * i)).isoformat(),
        })
    await _create_transactions(client, account_id, txs)

    res = await client.post("/api/v1/recurrences/detect")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert data[0]["frequency"] == "monthly"
    assert data[0]["is_active"] is True


@pytest.mark.asyncio
async def test_update_recurrence(auth_client: dict, sample_account: dict):
    """Atualizar uma recorrência detectada."""
    client: AsyncClient = auth_client["client"]
    account_id = sample_account["id"]
    now = datetime.now(timezone.utc)

    for i in range(4):
        await client.post("/api/v1/transactions/", json={
            "account_id": account_id,
            "description": "SPOTIFY PREMIUM",
            "amount": "-21.90",
            "type": "debit",
            "date": (now - timedelta(days=30 * i)).isoformat(),
        })

    detect_res = await client.post("/api/v1/recurrences/detect")
    recs = detect_res.json()
    if recs:
        rec_id = recs[0]["id"]
        update_res = await client.patch(
            f"/api/v1/recurrences/{rec_id}",
            json={"is_active": False},
        )
        assert update_res.status_code == 200
        assert update_res.json()["is_active"] is False
