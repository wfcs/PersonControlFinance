"""Service layer for account operations including Pluggy sync."""

from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.pluggy_client import PluggyClient
from app.models.account import Account
from app.models.transaction import Transaction

logger = logging.getLogger(__name__)

# Pluggy account type -> our account type mapping
_TYPE_MAP: dict[str, str] = {
    "BANK": "checking",
    "CREDIT": "credit_card",
    "INVESTMENT": "investment",
    "SAVINGS": "savings",
}


async def sync_from_pluggy(
    item_id: str,
    tenant_id: str,
    db: AsyncSession,
) -> dict:
    """Fetch accounts and transactions from Pluggy and upsert into DB.

    Returns a summary dict with counts of synced accounts and transactions.
    """
    client = PluggyClient()
    await client.authenticate()

    tid = UUID(tenant_id)
    accounts_synced = 0
    transactions_synced = 0

    # Fetch accounts from Pluggy
    pluggy_accounts = await client.get_accounts(item_id)
    for pa in pluggy_accounts:
        pluggy_id = pa.get("id", "")
        # Check if account already exists
        result = await db.execute(
            select(Account).where(
                Account.tenant_id == tid,
                Account.pluggy_account_id == pluggy_id,
            )
        )
        existing = result.scalar_one_or_none()

        acct_type = _TYPE_MAP.get(pa.get("type", ""), "checking")
        balance = Decimal(str(pa.get("balance", 0)))
        currency = pa.get("currencyCode", "BRL")
        name = pa.get("name", "Pluggy Account")
        institution = pa.get("institutionName", "")

        if existing:
            existing.balance = balance
            existing.name = name
            existing.institution = institution
        else:
            account = Account(
                name=name,
                type=acct_type,
                institution=institution,
                balance=balance,
                currency=currency,
                pluggy_account_id=pluggy_id,
                tenant_id=tid,
            )
            db.add(account)

        accounts_synced += 1

    await db.flush()

    # Fetch transactions for each pluggy account
    for pa in pluggy_accounts:
        pluggy_account_id = pa.get("id", "")
        # Find our local account
        result = await db.execute(
            select(Account).where(
                Account.tenant_id == tid,
                Account.pluggy_account_id == pluggy_account_id,
            )
        )
        local_account = result.scalar_one_or_none()
        if not local_account:
            continue

        pluggy_txns = await client.get_transactions(pluggy_account_id)
        for pt in pluggy_txns:
            amount_val = Decimal(str(abs(pt.get("amount", 0))))
            tx_type = "income" if pt.get("amount", 0) >= 0 else "expense"
            tx_date_str = pt.get("date", "")
            try:
                tx_date = date.fromisoformat(tx_date_str[:10])
            except (ValueError, IndexError):
                tx_date = date.today()

            transaction = Transaction(
                description=pt.get("description", "Pluggy Transaction"),
                amount=amount_val,
                type=tx_type,
                date=tx_date,
                account_id=local_account.id,
                tenant_id=tid,
            )
            db.add(transaction)
            transactions_synced += 1

    await db.commit()

    return {
        "accounts_synced": accounts_synced,
        "transactions_synced": transactions_synced,
    }
