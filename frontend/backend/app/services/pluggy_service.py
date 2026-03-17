"""Lógica de sincronização Open Finance via Pluggy."""

from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.integrations.pluggy_client import pluggy_client
from app.models.account import Account
from app.models.transaction import Transaction

logger = logging.getLogger(__name__)


# ── Connect Token ────────────────────────────────────────────────────────────


async def create_connect_token(
    tenant_id: UUID,
    user_id: UUID,
    db: AsyncSession,
    item_id: str | None = None,
) -> dict:
    """Gera Pluggy Connect Token para o widget no front-end."""
    client_user_id = f"{tenant_id}:{user_id}"
    return await pluggy_client.create_connect_token(
        item_id=item_id,
        webhook_url=settings.PLUGGY_WEBHOOK_URL,
        client_user_id=client_user_id,
    )


# ── Sync Accounts ───────────────────────────────────────────────────────────


async def sync_item_accounts(
    item_id: str, tenant_id: UUID, db: AsyncSession
) -> list[Account]:
    """Busca contas do Pluggy e faz upsert no banco local."""
    pluggy_accounts = await pluggy_client.get_accounts(item_id)
    synced: list[Account] = []

    for pa in pluggy_accounts:
        acc = await db.scalar(
            select(Account).where(
                Account.pluggy_account_id == pa["id"],
                Account.tenant_id == tenant_id,
            )
        )

        if acc:
            acc.balance = Decimal(str(pa.get("balance", 0)))
            acc.name = pa.get("name", acc.name)
            if pa.get("creditData") and pa["creditData"].get("creditLimit"):
                acc.credit_limit = Decimal(str(pa["creditData"]["creditLimit"]))
        else:
            connector = pa.get("connector") or {}
            acc = Account(
                tenant_id=tenant_id,
                name=pa.get("name", "Conta"),
                institution_name=connector.get("name", "Instituição"),
                institution_logo_url=connector.get("imageUrl"),
                type=_map_account_type(pa.get("type", "BANK")),
                pluggy_item_id=item_id,
                pluggy_account_id=pa["id"],
                balance=Decimal(str(pa.get("balance", 0))),
                credit_limit=(
                    Decimal(str(pa["creditData"]["creditLimit"]))
                    if pa.get("creditData") and pa["creditData"].get("creditLimit")
                    else None
                ),
            )
            db.add(acc)

        await db.flush()
        synced.append(acc)

    return synced


# ── Sync Transactions ────────────────────────────────────────────────────────


async def sync_item_transactions(
    item_id: str,
    tenant_id: UUID,
    db: AsyncSession,
    date_from: str | None = None,
) -> int:
    """Busca transações de todas as contas de um item e faz upsert."""
    accounts = (
        await db.scalars(
            select(Account).where(
                Account.pluggy_item_id == item_id,
                Account.tenant_id == tenant_id,
                Account.is_active.is_(True),
            )
        )
    ).all()

    total_synced = 0
    for acc in accounts:
        if not acc.pluggy_account_id:
            continue
        total_synced += await _sync_account_transactions(acc, tenant_id, db, date_from)

    return total_synced


async def _sync_account_transactions(
    account: Account,
    tenant_id: UUID,
    db: AsyncSession,
    date_from: str | None = None,
) -> int:
    """Pagina por todas as transações de uma conta e faz upsert."""
    page = 1
    synced = 0

    while True:
        result = await pluggy_client.get_transactions(
            account_id=account.pluggy_account_id,  # type: ignore[arg-type]
            date_from=date_from,
            page=page,
        )

        for pt in result.get("results", []):
            ext_id = pt["id"]
            existing = await db.scalar(
                select(Transaction).where(Transaction.external_id == ext_id)
            )

            if existing:
                existing.amount = Decimal(str(pt["amount"]))
                existing.description = pt.get("description", existing.description)
            else:
                tx = Transaction(
                    tenant_id=tenant_id,
                    account_id=account.id,
                    description=pt.get("description", ""),
                    amount=Decimal(str(pt["amount"])),
                    type=_map_tx_type(pt.get("type", "DEBIT")),
                    date=datetime.fromisoformat(pt["date"]),
                    external_id=ext_id,
                    installment_number=_extract_installment_number(pt),
                    installment_total=_extract_installment_total(pt),
                )
                db.add(tx)
                synced += 1

        await db.flush()

        if page >= result.get("totalPages", 1):
            break
        page += 1

    return synced


# ── Helpers ──────────────────────────────────────────────────────────────────


def _map_account_type(pluggy_type: str) -> str:
    return {
        "BANK": "checking",
        "CREDIT": "credit_card",
        "SAVINGS": "savings",
        "INVESTMENT": "investment",
    }.get(pluggy_type, "checking")


def _map_tx_type(pluggy_type: str) -> str:
    return {"DEBIT": "debit", "CREDIT": "credit"}.get(pluggy_type, "debit")


def _extract_installment_number(pt: dict) -> int | None:
    meta = pt.get("creditCardMetadata")
    if meta and meta.get("installmentNumber"):
        return meta["installmentNumber"]
    return None


def _extract_installment_total(pt: dict) -> int | None:
    meta = pt.get("creditCardMetadata")
    if meta and meta.get("totalInstallments"):
        return meta["totalInstallments"]
    return None
