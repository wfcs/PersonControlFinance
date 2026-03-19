from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


async def list_categories(tenant_id: UUID, session: AsyncSession) -> list[Category]:
    result = await session.execute(
        select(Category).where(Category.tenant_id == tenant_id).order_by(Category.name)
    )
    return list(result.scalars().all())


async def get_category(category_id: UUID, tenant_id: UUID, session: AsyncSession) -> Category:
    result = await session.execute(
        select(Category).where(Category.id == category_id, Category.tenant_id == tenant_id)
    )
    cat = result.scalar_one_or_none()
    if cat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return cat


async def create_category(
    data: CategoryCreate, tenant_id: UUID, session: AsyncSession
) -> Category:
    cat = Category(**data.model_dump(), tenant_id=tenant_id)
    session.add(cat)
    await session.flush()
    return cat


async def update_category(
    category_id: UUID, data: CategoryUpdate, tenant_id: UUID, session: AsyncSession
) -> Category:
    cat = await get_category(category_id, tenant_id, session)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cat, field, value)
    await session.flush()
    return cat


async def delete_category(category_id: UUID, tenant_id: UUID, session: AsyncSession) -> None:
    cat = await get_category(category_id, tenant_id, session)
    await session.delete(cat)
    await session.flush()
