"""Endpoints de recorrências."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from app.core.deps import AuthUser, DBSession
from app.schemas.recurrence import RecurrenceOut, RecurrenceUpdate
from app.services import recurrence_service

router = APIRouter(prefix="/recurrences", tags=["Recorrências"])


@router.get("/", response_model=list[RecurrenceOut])
async def list_recurrences(current_user: AuthUser, db: DBSession) -> list[RecurrenceOut]:
    recs = await recurrence_service.list_recurrences(current_user.tenant_id, db)
    return [RecurrenceOut.model_validate(r) for r in recs]


@router.post("/detect", response_model=list[RecurrenceOut])
async def detect_recurrences(current_user: AuthUser, db: DBSession) -> list[RecurrenceOut]:
    """Dispara algoritmo de detecção de recorrências."""
    recs = await recurrence_service.detect_recurrences(current_user.tenant_id, db)
    return [RecurrenceOut.model_validate(r) for r in recs]


@router.patch("/{rec_id}", response_model=RecurrenceOut)
async def update_recurrence(
    rec_id: UUID, data: RecurrenceUpdate, current_user: AuthUser, db: DBSession
) -> RecurrenceOut:
    rec = await recurrence_service.update_recurrence(rec_id, data, current_user.tenant_id, db)
    return RecurrenceOut.model_validate(rec)
