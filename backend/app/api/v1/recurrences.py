from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.recurrence import RecurrenceCreate, RecurrenceResponse, RecurrenceUpdate
from app.schemas.transaction import TransactionResponse
from app.services.recurrence_service import (
    create_recurrence,
    delete_recurrence,
    detect_recurrences,
    get_recurrence,
    list_recurrences,
    process_due_recurrences,
    update_recurrence,
)

router = APIRouter(prefix="/recurrences", tags=["Recurrences"])


@router.get("", response_model=list[RecurrenceResponse])
async def list_all(
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[RecurrenceResponse]:
    recs = await list_recurrences(current_user.tenant_id, session, active_only=active_only)
    return [RecurrenceResponse.model_validate(r) for r in recs]


@router.get("/{recurrence_id}", response_model=RecurrenceResponse)
async def get_one(
    recurrence_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> RecurrenceResponse:
    rec = await get_recurrence(recurrence_id, current_user.tenant_id, session)
    return RecurrenceResponse.model_validate(rec)


@router.post("", response_model=RecurrenceResponse, status_code=201)
async def create(
    data: RecurrenceCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> RecurrenceResponse:
    rec = await create_recurrence(data, current_user.tenant_id, session)
    return RecurrenceResponse.model_validate(rec)


@router.patch("/{recurrence_id}", response_model=RecurrenceResponse)
async def update(
    recurrence_id: UUID,
    data: RecurrenceUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> RecurrenceResponse:
    rec = await update_recurrence(recurrence_id, data, current_user.tenant_id, session)
    return RecurrenceResponse.model_validate(rec)


@router.delete("/{recurrence_id}", status_code=204)
async def delete(
    recurrence_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    await delete_recurrence(recurrence_id, current_user.tenant_id, session)


@router.post("/process", response_model=list[TransactionResponse])
async def process_due(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[TransactionResponse]:
    """Process all due recurrences and create transactions."""
    txns = await process_due_recurrences(current_user.tenant_id, session)
    return [TransactionResponse.model_validate(t) for t in txns]


@router.post("/detect", response_model=list[RecurrenceResponse])
async def detect(
    months: int = 6,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[RecurrenceResponse]:
    """Detect recurring patterns from transaction history."""
    recs = await detect_recurrences(current_user.tenant_id, session, months=months)
    return [RecurrenceResponse.model_validate(r) for r in recs]
