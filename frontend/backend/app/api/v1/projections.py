"""Endpoints de projeção de saldo."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.core.deps import AuthUser, DBSession
from app.services import projection_service

router = APIRouter(prefix="/projections", tags=["Projeções"])


@router.get("/balance")
async def get_balance_projection(
    current_user: AuthUser,
    db: DBSession,
    months: int = Query(3, ge=1, le=12, description="Meses de projeção (1-12)"),
) -> list[dict]:
    """Projeção de saldo para os próximos N meses."""
    return await projection_service.project_balance(
        current_user.tenant_id, db, months
    )
