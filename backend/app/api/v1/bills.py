"""Endpoints de faturas de cartão de crédito."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Query

from app.core.deps import AuthUser, DBSession
from app.services import bill_service

router = APIRouter(prefix="/bills", tags=["Faturas"])


@router.get("/{account_id}")
async def get_bills(
    account_id: UUID,
    current_user: AuthUser,
    db: DBSession,
    closing_day: int = Query(25, ge=1, le=31, description="Dia de fechamento da fatura"),
) -> list[dict]:
    """Lista faturas do cartão agrupadas por ciclo."""
    return await bill_service.get_credit_card_bills(
        current_user.tenant_id, account_id, db, closing_day
    )
