from __future__ import annotations

from datetime import date

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.cashflow import CashFlowResponse
from app.services.cashflow_service import get_cash_flow

router = APIRouter(prefix="/cashflow", tags=["Cash Flow"])


@router.get("", response_model=CashFlowResponse)
async def cash_flow(
    months: int = Query(default=6, ge=1, le=24),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> CashFlowResponse:
    """Get income vs expense aggregated by month."""
    date_to = date.today()
    date_from = date_to - relativedelta(months=months)
    return await get_cash_flow(current_user.tenant_id, session, date_from, date_to)
