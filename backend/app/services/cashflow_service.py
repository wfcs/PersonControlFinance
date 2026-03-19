from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction
from app.schemas.cashflow import CashFlowPeriod, CashFlowResponse


async def get_cash_flow(
    tenant_id: UUID,
    session: AsyncSession,
    date_from: date,
    date_to: date,
) -> CashFlowResponse:
    """Aggregate income/expense by month between date_from and date_to."""
    result = await session.execute(
        select(
            func.strftime("%Y-%m", Transaction.date).label("period"),
            Transaction.type,
            func.sum(Transaction.amount).label("total"),
        )
        .where(
            Transaction.tenant_id == tenant_id,
            Transaction.date >= date_from,
            Transaction.date <= date_to,
        )
        .group_by("period", Transaction.type)
        .order_by("period")
    )
    rows = result.all()

    # Build period map
    period_map: dict[str, dict[str, Decimal]] = {}
    for row in rows:
        period = row.period
        if period not in period_map:
            period_map[period] = {"income": Decimal("0"), "expense": Decimal("0")}
        if row.type in ("income", "receita"):
            period_map[period]["income"] += Decimal(str(row.total))
        else:
            period_map[period]["expense"] += Decimal(str(row.total))

    periods = []
    total_income = Decimal("0")
    total_expense = Decimal("0")
    for period_key in sorted(period_map.keys()):
        data = period_map[period_key]
        net = data["income"] - data["expense"]
        periods.append(
            CashFlowPeriod(
                period=period_key,
                income=data["income"],
                expense=data["expense"],
                net=net,
            )
        )
        total_income += data["income"]
        total_expense += data["expense"]

    return CashFlowResponse(
        periods=periods,
        total_income=total_income,
        total_expense=total_expense,
        total_net=total_income - total_expense,
        date_from=date_from,
        date_to=date_to,
    )
