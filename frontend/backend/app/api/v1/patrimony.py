"""Endpoints de patrimônio."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.core.deps import AuthUser, DBSession
from app.services import patrimony_service

router = APIRouter(prefix="/patrimony", tags=["Patrimônio"])


@router.get("/net-worth")
async def get_net_worth(current_user: AuthUser, db: DBSession) -> dict:
    """Patrimônio líquido atual: ativos, passivos e breakdown por tipo."""
    return await patrimony_service.get_net_worth(current_user.tenant_id, db)


@router.get("/history")
async def get_net_worth_history(
    current_user: AuthUser,
    db: DBSession,
    months: int = Query(6, ge=1, le=24, description="Meses de histórico"),
) -> list[dict]:
    """Evolução histórica do patrimônio líquido."""
    return await patrimony_service.get_net_worth_history(
        current_user.tenant_id, db, months
    )
