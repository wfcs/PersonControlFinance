from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


async def list_categories(tenant_id: UUID, db: AsyncSession) -> list[Category]:
    """Retorna apenas categorias raiz com seus filhos carregados."""
    rows = (
        await db.scalars(
            select(Category)
            .where(Category.tenant_id == tenant_id, Category.parent_id.is_(None))
            .options(selectinload(Category.children))
            .order_by(Category.name)
        )
    ).all()
    return list(rows)


async def get_category(cat_id: UUID, tenant_id: UUID, db: AsyncSession) -> Category:
    cat = await db.scalar(
        select(Category).where(Category.id == cat_id, Category.tenant_id == tenant_id)
    )
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada")
    return cat


async def create_category(data: CategoryCreate, tenant_id: UUID, db: AsyncSession) -> Category:
    cat = Category(**data.model_dump(), tenant_id=tenant_id)
    db.add(cat)
    await db.flush()
    await db.refresh(cat)
    return cat


async def update_category(
    cat_id: UUID, data: CategoryUpdate, tenant_id: UUID, db: AsyncSession
) -> Category:
    cat = await get_category(cat_id, tenant_id, db)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(cat, field, value)
    await db.flush()
    await db.refresh(cat)
    return cat


async def delete_category(cat_id: UUID, tenant_id: UUID, db: AsyncSession) -> None:
    cat = await get_category(cat_id, tenant_id, db)
    await db.delete(cat)
