from __future__ import annotations

import logging
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.transaction import Transaction
from app.services import pluggy_client

logger = logging.getLogger(__name__)


async def sync_item_accounts(
    item_id: str,
    tenant_id: UUID,
    session: AsyncSession,
) -> list[Account]:
    """Sync accounts from Pluggy item into our database.

    Creates new accounts or updates existing ones.
    Returns list of synced accounts.
    """
    pluggy_accounts = await pluggy_client.get_item_accounts(item_id)
    synced: list[Account] = []

    for pa in pluggy_accounts:
        pluggy_account_id = pa["id"]

        # Check if account already exists
        result = await session.execute(
            select(Account).where(
                Account.tenant_id == tenant_id,
                Account.pluggy_item_id == pluggy_account_id,
            )
        )
        account = result.scalar_one_or_none()

        balance = Decimal(str(pa.get("balance", 0)))
        name = pa.get("name", "Conta Bancária")
        acc_type = _map_account_type(pa.get("type", "BANK"))
        bank_name = pa.get("bankData", {}).get("transferNumber", "") if pa.get("bankData") else ""
        currency = pa.get("currencyCode", "BRL")

        if account:
            # Update existing
            account.name = name
            account.balance = balance
            account.bank_name = bank_name or account.bank_name
            account.currency = currency
        else:
            # Create new
            account = Account(
                name=name,
                type=acc_type,
                bank_name=bank_name,
                balance=balance,
                currency=currency,
                pluggy_item_id=pluggy_account_id,
                tenant_id=tenant_id,
            )
            session.add(account)

        synced.append(account)

    await session.flush()
    return synced


async def sync_item_transactions(
    item_id: str,
    tenant_id: UUID,
    session: AsyncSession,
    days_back: int = 90,
) -> int:
    """Sync transactions from all accounts of a Pluggy item.

    Returns number of new transactions created.
    """
    # Get our accounts linked to this item
    pluggy_accounts = await pluggy_client.get_item_accounts(item_id)
    total_created = 0

    date_from = (date.today() - timedelta(days=days_back)).isoformat()

    for pa in pluggy_accounts:
        pluggy_account_id = pa["id"]

        # Find our local account
        result = await session.execute(
            select(Account).where(
                Account.tenant_id == tenant_id,
                Account.pluggy_item_id == pluggy_account_id,
            )
        )
        account = result.scalar_one_or_none()
        if not account:
            continue

        # Fetch transactions from Pluggy (paginated)
        page = 1
        while True:
            data = await pluggy_client.get_account_transactions(
                pluggy_account_id, date_from=date_from, page=page
            )
            transactions = data.get("results", [])
            if not transactions:
                break

            for pt in transactions:
                pluggy_txn_id = pt["id"]

                # Check if already imported (using description + date + amount as key)
                txn_date = date.fromisoformat(pt["date"][:10])
                amount = abs(Decimal(str(pt.get("amount", 0))))
                description = pt.get("description", "")[:500]
                txn_type = "income" if pt.get("amount", 0) >= 0 else "expense"

                # Simple dedup: check if same desc+date+amount exists
                existing = await session.execute(
                    select(Transaction).where(
                        Transaction.tenant_id == tenant_id,
                        Transaction.account_id == account.id,
                        Transaction.date == txn_date,
                        Transaction.amount == amount,
                        Transaction.description == description,
                    )
                )
                if existing.scalar_one_or_none():
                    continue

                txn = Transaction(
                    description=description or "Transação importada",
                    amount=amount,
                    type=txn_type,
                    date=txn_date,
                    account_id=account.id,
                    tenant_id=tenant_id,
                    is_recurring=False,
                    notes=f"Importado via Pluggy (ID: {pluggy_txn_id})",
                )
                session.add(txn)
                total_created += 1

            # Check if there are more pages
            total_pages = data.get("totalPages", 1)
            if page >= total_pages:
                break
            page += 1

    await session.flush()
    return total_created


async def sync_full_item(
    item_id: str,
    tenant_id: UUID,
    session: AsyncSession,
) -> dict:
    """Full sync: accounts + transactions for a Pluggy item."""
    accounts = await sync_item_accounts(item_id, tenant_id, session)
    txn_count = await sync_item_transactions(item_id, tenant_id, session)
    return {
        "accounts_synced": len(accounts),
        "transactions_imported": txn_count,
    }


def _map_account_type(pluggy_type: str) -> str:
    """Map Pluggy account type to our internal types."""
    mapping = {
        "BANK": "checking",
        "CREDIT": "credit_card",
        "INVESTMENT": "investment",
        "SAVINGS": "savings",
    }
    return mapping.get(pluggy_type.upper(), "checking")
