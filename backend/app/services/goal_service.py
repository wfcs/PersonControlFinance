from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.goal import Goal
from app.schemas.goal import GoalCreate, GoalUpdate


async def list_goals(tenant_id: UUID, session: AsyncSession) -> list[Goal]:
    result = await session.execute(
        select(Goal).where(Goal.tenant_id == tenant_id).order_by(Goal.created_at.desc())
    )
    return list(result.scalars().all())


async def get_goal(goal_id: UUID, tenant_id: UUID, session: AsyncSession) -> Goal:
    result = await session.execute(
        select(Goal).where(Goal.id == goal_id, Goal.tenant_id == tenant_id)
    )
    goal = result.scalar_one_or_none()
    if goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return goal


async def create_goal(data: GoalCreate, tenant_id: UUID, session: AsyncSession) -> Goal:
    goal = Goal(**data.model_dump(), tenant_id=tenant_id)
    session.add(goal)
    await session.flush()
    return goal


async def update_goal(
    goal_id: UUID, data: GoalUpdate, tenant_id: UUID, session: AsyncSession
) -> Goal:
    goal = await get_goal(goal_id, tenant_id, session)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(goal, field, value)
    await session.flush()
    return goal


async def delete_goal(goal_id: UUID, tenant_id: UUID, session: AsyncSession) -> None:
    goal = await get_goal(goal_id, tenant_id, session)
    await session.delete(goal)
    await session.flush()
