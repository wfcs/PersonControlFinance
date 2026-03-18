"""Goal CRUD endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.core.plan_guard import check_resource_limit
from app.models.goal import Goal
from app.models.user import User
from app.schemas.goal import GoalCreate, GoalRead, GoalUpdate

router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("", response_model=list[GoalRead])
async def list_goals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all goals for the current tenant."""
    result = await db.execute(
        select(Goal).where(Goal.tenant_id == current_user.tenant_id).order_by(Goal.created_at.desc())
    )
    return list(result.scalars().all())


@router.post("", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
async def create_goal(
    payload: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new goal (checks plan limit)."""
    await check_resource_limit(db, current_user.tenant_id, "goals", Goal)

    goal = Goal(
        name=payload.name,
        target_amount=payload.target_amount,
        deadline=payload.deadline,
        tenant_id=current_user.tenant_id,
    )
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    return goal


@router.get("/{goal_id}", response_model=GoalRead)
async def get_goal(
    goal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a goal by ID."""
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id, Goal.tenant_id == current_user.tenant_id)
    )
    goal = result.scalar_one_or_none()
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal


@router.put("/{goal_id}", response_model=GoalRead)
async def update_goal(
    goal_id: UUID,
    payload: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a goal (including current_amount for progress tracking)."""
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id, Goal.tenant_id == current_user.tenant_id)
    )
    goal = result.scalar_one_or_none()
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goal, field, value)

    await db.commit()
    await db.refresh(goal)
    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_200_OK)
async def delete_goal(
    goal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a goal."""
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id, Goal.tenant_id == current_user.tenant_id)
    )
    goal = result.scalar_one_or_none()
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")

    await db.delete(goal)
    await db.commit()
    return {"detail": "Goal deleted"}
