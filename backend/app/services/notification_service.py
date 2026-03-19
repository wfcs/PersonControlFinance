from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.schemas.notification import NotificationCreate


async def list_notifications(
    user_id: UUID,
    tenant_id: UUID,
    session: AsyncSession,
    unread_only: bool = False,
    limit: int = 50,
) -> list[Notification]:
    query = select(Notification).where(
        Notification.user_id == user_id,
        Notification.tenant_id == tenant_id,
    )
    if unread_only:
        query = query.where(Notification.is_read == False)  # noqa: E712
    query = query.order_by(Notification.created_at.desc()).limit(limit)
    result = await session.execute(query)
    return list(result.scalars().all())


async def create_notification(
    user_id: UUID,
    tenant_id: UUID,
    data: NotificationCreate,
    session: AsyncSession,
) -> Notification:
    notif = Notification(
        user_id=user_id,
        tenant_id=tenant_id,
        **data.model_dump(),
    )
    session.add(notif)
    await session.flush()
    return notif


async def mark_as_read(
    notification_id: UUID,
    user_id: UUID,
    session: AsyncSession,
) -> None:
    result = await session.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
    )
    notif = result.scalar_one_or_none()
    if notif is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    notif.is_read = True
    await session.flush()


async def mark_all_as_read(
    user_id: UUID,
    tenant_id: UUID,
    session: AsyncSession,
) -> int:
    result = await session.execute(
        update(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.tenant_id == tenant_id,
            Notification.is_read == False,  # noqa: E712
        )
        .values(is_read=True)
    )
    await session.flush()
    return result.rowcount
