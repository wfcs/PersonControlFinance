from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class CashFlowPeriod(BaseModel):
    period: str  # "2026-01", "2026-02", etc.
    income: Decimal
    expense: Decimal
    net: Decimal


class CashFlowResponse(BaseModel):
    periods: list[CashFlowPeriod]
    total_income: Decimal
    total_expense: Decimal
    total_net: Decimal
    date_from: date
    date_to: date


class ProjectionPoint(BaseModel):
    date: date
    projected_balance: Decimal
    includes_recurring: bool = True


class ProjectionResponse(BaseModel):
    current_balance: Decimal
    points: list[ProjectionPoint]
    lowest_balance: Decimal
    lowest_balance_date: Optional[date]


class NetWorthEntry(BaseModel):
    period: str
    assets: Decimal
    liabilities: Decimal
    net_worth: Decimal


class NetWorthResponse(BaseModel):
    current_assets: Decimal
    current_liabilities: Decimal
    current_net_worth: Decimal
    history: list[NetWorthEntry]
