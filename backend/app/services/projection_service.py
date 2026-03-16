"""Projeção de saldo futuro baseada em recorrências ativas."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from dateutil.relativedelta import relativedelta
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.recurrence import Recurrence


async def project_balance(
    tenant_id: UUID,
    db: AsyncSession,
    months: int = 3,
) -> list[dict]:
    """
    Projeta saldo para os próximos N meses com base em:
    - Saldo total atual de todas as contas
    - Recorrências mensais ativas (despesas fixas)
    - Parcelas restantes (installments)
    """
    total_balance = (
        await db.scalar(
            select(func.sum(Account.balance)).where(
                Account.tenant_id == tenant_id,
                Account.is_active.is_(True),
            )
        )
    ) or Decimal("0")

    recurrences = (
        await db.scalars(
            select(Recurrence).where(
                Recurrence.tenant_id == tenant_id,
                Recurrence.is_active.is_(True),
            )
        )
    ).all()

    projections: list[dict] = []
    current_balance = total_balance
    today = date.today()

    for i in range(1, months + 1):
        target_month = today + relativedelta(months=i)
        month_expenses = Decimal("0")
        month_income = Decimal("0")

        for rec in recurrences:
            if rec.frequency == "monthly":
                month_expenses += rec.amount
            elif rec.frequency == "installment":
                if rec.current_installment and rec.total_installments:
                    remaining = rec.total_installments - rec.current_installment
                    if i <= remaining:
                        month_expenses += rec.amount

        month_delta = month_income - month_expenses
        current_balance += month_delta

        projections.append({
            "month": target_month.strftime("%Y-%m"),
            "projected_balance": float(current_balance),
            "monthly_expenses": float(month_expenses),
            "monthly_income": float(month_income),
            "monthly_delta": float(month_delta),
            "alert": current_balance < 0,
        })

    return projections
