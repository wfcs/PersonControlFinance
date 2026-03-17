"""Agrupamento de transações de cartão de crédito por ciclo de fatura."""

from __future__ import annotations

from datetime import datetime, date, timedelta
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.transaction import Transaction


async def get_credit_card_bills(
    tenant_id: UUID,
    account_id: UUID,
    db: AsyncSession,
    closing_day: int = 25,
) -> list[dict]:
    """Agrupa transações do cartão por ciclo de fatura."""
    account = await db.scalar(
        select(Account).where(
            Account.id == account_id,
            Account.tenant_id == tenant_id,
            Account.type == "credit_card",
        )
    )
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta de cartão de crédito não encontrada",
        )

    transactions = (
        await db.scalars(
            select(Transaction)
            .where(
                Transaction.account_id == account_id,
                Transaction.tenant_id == tenant_id,
                Transaction.is_excluded.is_(False),
            )
            .order_by(Transaction.date.desc())
        )
    ).all()

    bills: dict[str, dict] = {}
    for tx in transactions:
        bill_key = _get_bill_period(tx.date, closing_day)
        if bill_key not in bills:
            closing = _get_closing_date(tx.date, closing_day)
            bills[bill_key] = {
                "period": bill_key,
                "closing_date": closing.isoformat(),
                "due_date": (closing + timedelta(days=10)).isoformat(),
                "total": Decimal("0"),
                "transaction_count": 0,
                "installment_total": Decimal("0"),
                "recurring_total": Decimal("0"),
            }

        bills[bill_key]["total"] += tx.amount
        bills[bill_key]["transaction_count"] += 1

        if tx.installment_total:
            bills[bill_key]["installment_total"] += tx.amount
        elif tx.recurrence_id:
            bills[bill_key]["recurring_total"] += tx.amount

    return sorted(bills.values(), key=lambda b: b["period"], reverse=True)


def _get_bill_period(tx_date: datetime, closing_day: int) -> str:
    """Determina a qual período de fatura uma transação pertence."""
    d = tx_date.date() if isinstance(tx_date, datetime) else tx_date
    if d.day <= closing_day:
        return f"{d.year}-{d.month:02d}"
    else:
        next_month = d.replace(day=1) + timedelta(days=32)
        return f"{next_month.year}-{next_month.month:02d}"


def _get_closing_date(tx_date: datetime, closing_day: int) -> date:
    d = tx_date.date() if isinstance(tx_date, datetime) else tx_date
    if d.day <= closing_day:
        return d.replace(day=min(closing_day, 28))
    else:
        next_month = d.replace(day=1) + timedelta(days=32)
        return next_month.replace(day=min(closing_day, 28))
