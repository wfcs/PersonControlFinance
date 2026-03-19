from __future__ import annotations

import pytest
from httpx import AsyncClient


async def _setup(client: AsyncClient) -> tuple[str, str]:
    """Register, login, create credit card account."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "inv@example.com",
            "full_name": "Inv User",
            "password": "strongpass123",
            "tenant_name": "Inv Corp",
        },
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "inv@example.com", "password": "strongpass123"},
    )
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post(
        "/api/v1/accounts",
        json={"name": "Nubank CC", "type": "credit_card", "balance": "0.00"},
        headers=headers,
    )
    account_id = resp.json()["id"]
    return token, account_id


@pytest.mark.asyncio
async def test_invoice_crud(client: AsyncClient) -> None:
    token, account_id = await _setup(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create
    resp = await client.post(
        "/api/v1/invoices",
        json={
            "credit_card_account_id": account_id,
            "due_date": "2026-04-10",
            "close_date": "2026-04-03",
            "total_amount": "1500.00",
            "status": "open",
        },
        headers=headers,
    )
    assert resp.status_code == 201
    inv_id = resp.json()["id"]

    # List
    resp = await client.get("/api/v1/invoices", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

    # Update
    resp = await client.patch(
        f"/api/v1/invoices/{inv_id}",
        json={"status": "paid"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "paid"

    # Delete
    resp = await client.delete(f"/api/v1/invoices/{inv_id}", headers=headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_invoices_filter_by_account(client: AsyncClient) -> None:
    token, account_id = await _setup(client)
    headers = {"Authorization": f"Bearer {token}"}

    await client.post(
        "/api/v1/invoices",
        json={
            "credit_card_account_id": account_id,
            "due_date": "2026-05-10",
            "close_date": "2026-05-03",
        },
        headers=headers,
    )

    resp = await client.get(
        f"/api/v1/invoices?account_id={account_id}", headers=headers
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_invoices_require_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/invoices")
    assert resp.status_code in (401, 403)
