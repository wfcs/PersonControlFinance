from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.services.notification_service import (
    list_notifications,
    mark_all_as_read,
    mark_as_read,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationResponse])
async def list_all(
    unread_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[NotificationResponse]:
    notifs = await list_notifications(
        current_user.id, current_user.tenant_id, session,
        unread_only=unread_only, limit=limit,
    )
    return [NotificationResponse.model_validate(n) for n in notifs]


@router.patch("/{notification_id}/read", status_code=204)
async def read_one(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    await mark_as_read(notification_id, current_user.id, session)


@router.post("/read-all", status_code=200)
async def read_all(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    count = await mark_all_as_read(current_user.id, current_user.tenant_id, session)
    return {"marked_as_read": count}
