"""Cálculos de patrimônio líquido (ativos vs passivos)."""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.transaction import Transaction


async def get_net_worth(tenant_id: UUID, db: AsyncSession) -> dict:
    """Retorna ativos, passivos, patrimônio líquido e breakdown por tipo."""
    accounts = (
        await db.scalars(
            select(Account).where(
                Account.tenant_id == tenant_id,
                Account.is_active.is_(True),
            )
        )
    ).all()

    assets = Decimal("0")
    liabilities = Decimal("0")
    by_type: dict[str, float] = {}

    for acc in accounts:
        balance = acc.balance or Decimal("0")
        if acc.type in ("checking", "savings", "investment", "wallet"):
            if balance > 0:
                assets += balance
        elif acc.type == "credit_card":
            liabilities += abs(balance)

        by_type.setdefault(acc.type, 0.0)
        by_type[acc.type] += float(balance)

    net_worth = assets - liabilities
    return {
        "assets": float(assets),
        "liabilities": float(liabilities),
        "net_worth": float(net_worth),
        "by_type": by_type,
    }


async def get_net_worth_history(
    tenant_id: UUID, db: AsyncSession, months: int = 6
) -> list[dict]:
    """
    Histórico de patrimônio líquido por mês.
    Reconstrói saldo a partir do saldo atual e transações mensais.
    """
    accounts = (
        await db.scalars(
            select(Account).where(
                Account.tenant_id == tenant_id,
                Account.is_active.is_(True),
            )
        )
    ).all()

    current_total = sum((acc.balance or Decimal("0")) for acc in accounts)
    now = datetime.utcnow()

    history: list[dict] = []

    for i in range(months, -1, -1):
        if i == 0:
            history.append({
                "month": now.strftime("%Y-%m"),
                "net_worth": float(current_total),
            })
            continue

        month_start = datetime(now.year, now.month, 1) - timedelta(days=30 * i)
        month_end = datetime(now.year, now.month, 1) - timedelta(days=30 * (i - 1))

        month_delta = (
            await db.scalar(
                select(func.sum(Transaction.amount)).where(
                    Transaction.tenant_id == tenant_id,
                    Transaction.date >= month_end,
                    Transaction.date < now,
                    Transaction.is_excluded.is_(False),
                )
            )
        ) or Decimal("0")

        balance_at_month = current_total - month_delta
        history.append({
            "month": month_start.strftime("%Y-%m"),
            "net_worth": float(balance_at_month),
        })

    return history
