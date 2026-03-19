from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.cashflow import ProjectionResponse
from app.services.projection_service import get_balance_projection

router = APIRouter(prefix="/projection", tags=["Projection"])


@router.get("", response_model=ProjectionResponse)
async def projection(
    months: int = Query(default=6, ge=1, le=24),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ProjectionResponse:
    """Project future balance based on current balance and recurring transactions."""
    return await get_balance_projection(current_user.tenant_id, session, months_ahead=months)
