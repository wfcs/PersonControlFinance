from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.cashflow import NetWorthResponse
from app.services.networth_service import get_net_worth

router = APIRouter(prefix="/networth", tags=["Net Worth"])


@router.get("", response_model=NetWorthResponse)
async def net_worth(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> NetWorthResponse:
    """Calculate current net worth (assets - liabilities)."""
    return await get_net_worth(current_user.tenant_id, session)
