from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.recurrence import Recurrence
from app.schemas.cashflow import ProjectionPoint, ProjectionResponse
from app.services.recurrence_service import _advance_date


async def get_balance_projection(
    tenant_id: UUID,
    session: AsyncSession,
    months_ahead: int = 6,
) -> ProjectionResponse:
    """Project future balance based on current balance + recurring transactions."""
    # Get current total balance
    result = await session.execute(
        select(func.coalesce(func.sum(Account.balance), Decimal("0"))).where(
            Account.tenant_id == tenant_id
        )
    )
    current_balance = Decimal(str(result.scalar()))

    # Get active recurrences
    result = await session.execute(
        select(Recurrence).where(
            Recurrence.tenant_id == tenant_id,
            Recurrence.is_active == True,  # noqa: E712
        )
    )
    recurrences = list(result.scalars().all())

    # Project forward
    today = date.today()
    end_date = today + timedelta(days=months_ahead * 30)
    points: list[ProjectionPoint] = []
    running_balance = current_balance

    # Generate monthly projection points
    current_date = today
    lowest_balance = current_balance
    lowest_balance_date: Optional[date] = today

    while current_date <= end_date:
        month_delta = Decimal("0")

        for rec in recurrences:
            # Count how many times this recurrence hits in this month
            rec_date = rec.next_due_date
            while rec_date <= current_date + timedelta(days=30) and rec_date > current_date:
                if rec.type in ("income", "receita"):
                    month_delta += rec.amount
                else:
                    month_delta -= rec.amount
                rec_date = _advance_date(rec_date, rec.frequency)

        running_balance += month_delta
        points.append(
            ProjectionPoint(
                date=current_date,
                projected_balance=running_balance,
            )
        )

        if running_balance < lowest_balance:
            lowest_balance = running_balance
            lowest_balance_date = current_date

        current_date += timedelta(days=30)

    return ProjectionResponse(
        current_balance=current_balance,
        points=points,
        lowest_balance=lowest_balance,
        lowest_balance_date=lowest_balance_date,
    )
