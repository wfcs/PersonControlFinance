from datetime import datetime, timezone

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dashboard_summary_empty(auth_client: dict):
    client: AsyncClient = auth_client["client"]
    now = datetime.now(timezone.utc)
    res = await client.get(f"/api/v1/dashboard/summary?year={now.year}&month={now.month}")
    assert res.status_code == 200
    data = res.json()
    assert "summary" in data
    assert "spending_by_category" in data
    assert "recent_transactions" in data
    assert float(data["summary"]["receita"]) == 0.0


@pytest.mark.asyncio
async def test_dashboard_summary_with_data(auth_client: dict, sample_account: dict):
    client: AsyncClient = auth_client["client"]
    now = datetime.now(timezone.utc)

    # Receita
    await client.post("/api/v1/transactions/", json={
        "account_id": sample_account["id"],
        "description": "Salário",
        "amount": "6000.00",
        "type": "credit",
        "date": now.isoformat(),
    })
    # Despesa
    await client.post("/api/v1/transactions/", json={
        "account_id": sample_account["id"],
        "description": "Aluguel",
        "amount": "-1500.00",
        "type": "debit",
        "date": now.isoformat(),
    })

    res = await client.get(f"/api/v1/dashboard/summary?year={now.year}&month={now.month}")
    assert res.status_code == 200
    summary = res.json()["summary"]
    assert float(summary["receita"]) == 6000.00
    assert float(summary["gasto"]) == 1500.00
    assert float(summary["resultado"]) == 4500.00


@pytest.mark.asyncio
async def test_cash_flow(auth_client: dict):
    client: AsyncClient = auth_client["client"]
    res = await client.get("/api/v1/dashboard/cash-flow?months=3")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 3
    assert all("year" in d and "month" in d and "receita" in d for d in data)
