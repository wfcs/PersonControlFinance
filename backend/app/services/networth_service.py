from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.schemas.cashflow import NetWorthEntry, NetWorthResponse


# Account types classified as liabilities
LIABILITY_TYPES = {"credit_card", "cartao_credito", "loan", "emprestimo", "financing", "financiamento"}


async def get_net_worth(
    tenant_id: UUID,
    session: AsyncSession,
) -> NetWorthResponse:
    """Calculate net worth from account balances (assets - liabilities)."""
    result = await session.execute(
        select(Account).where(Account.tenant_id == tenant_id)
    )
    accounts = list(result.scalars().all())

    assets = Decimal("0")
    liabilities = Decimal("0")

    for account in accounts:
        if account.type.lower() in LIABILITY_TYPES:
            liabilities += abs(account.balance)
        else:
            assets += account.balance

    # For now, history returns a single current-month entry
    # Future: store monthly snapshots for historical tracking
    today = date.today()
    current_period = today.strftime("%Y-%m")

    return NetWorthResponse(
        current_assets=assets,
        current_liabilities=liabilities,
        current_net_worth=assets - liabilities,
        history=[
            NetWorthEntry(
                period=current_period,
                assets=assets,
                liabilities=liabilities,
                net_worth=assets - liabilities,
            )
        ],
    )
