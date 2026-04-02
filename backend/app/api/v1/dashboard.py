from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_session
from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


class DashboardSummary(BaseModel):
    totalBalance: float
    totalIncome: float
    totalExpenses: float
    savingsRate: float


class SpendingByCategory(BaseModel):
    category: str
    amount: float
    color: str
    percentage: float


@router.get("/summary", response_model=DashboardSummary)
async def get_summary(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> DashboardSummary:
    tenant_id = current_user.tenant_id

    # Total balance across all accounts
    balance_result = await session.execute(
        select(func.coalesce(func.sum(Account.balance), Decimal("0")))
        .where(Account.tenant_id == tenant_id)
    )
    total_balance = float(balance_result.scalar() or 0)

    # Current month income and expenses
    today = date.today()
    first_day = today.replace(day=1)

    income_result = await session.execute(
        select(func.coalesce(func.sum(Transaction.amount), Decimal("0")))
        .where(
            Transaction.tenant_id == tenant_id,
            Transaction.type == "income",
            Transaction.date >= first_day,
            Transaction.date <= today,
        )
    )
    total_income = float(income_result.scalar() or 0)

    expense_result = await session.execute(
        select(func.coalesce(func.sum(Transaction.amount), Decimal("0")))
        .where(
            Transaction.tenant_id == tenant_id,
            Transaction.type == "expense",
            Transaction.date >= first_day,
            Transaction.date <= today,
        )
    )
    total_expenses = float(expense_result.scalar() or 0)

    savings_rate = 0.0
    if total_income > 0:
        savings_rate = ((total_income - total_expenses) / total_income) * 100

    return DashboardSummary(
        totalBalance=total_balance,
        totalIncome=total_income,
        totalExpenses=total_expenses,
        savingsRate=round(savings_rate, 1),
    )


@router.get("/spending-by-category", response_model=list[SpendingByCategory])
async def get_spending_by_category(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[SpendingByCategory]:
    tenant_id = current_user.tenant_id
    today = date.today()
    first_day = today.replace(day=1)

    # Get expenses grouped by category for current month
    result = await session.execute(
        select(
            Category.name,
            Category.color,
            func.coalesce(func.sum(Transaction.amount), Decimal("0")).label("total"),
        )
        .join(Category, Transaction.category_id == Category.id, isouter=True)
        .where(
            Transaction.tenant_id == tenant_id,
            Transaction.type == "expense",
            Transaction.date >= first_day,
            Transaction.date <= today,
        )
        .group_by(Category.name, Category.color)
        .order_by(func.sum(Transaction.amount).desc())
        .limit(10)
    )
    rows = result.all()

    if not rows:
        return []

    total = sum(float(r.total) for r in rows)
    default_colors = ["#f97316", "#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444", "#06b6d4", "#ec4899", "#84cc16", "#6366f1"]

    items = []
    for i, row in enumerate(rows):
        amount = float(row.total)
        items.append(SpendingByCategory(
            category=row.name or "Sem categoria",
            amount=amount,
            color=row.color or default_colors[i % len(default_colors)],
            percentage=round((amount / total) * 100, 1) if total > 0 else 0,
        ))
    return items


@router.post("/complete-onboarding")
async def complete_onboarding(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    current_user.has_completed_onboarding = True
    session.add(current_user)
    await session.flush()
    return {"status": "success"}
