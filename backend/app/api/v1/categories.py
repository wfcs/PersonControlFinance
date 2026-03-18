"""Category CRUD endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user, get_db
from app.core.plan_guard import check_resource_limit
from app.models.category import Category
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


def _category_to_read(cat: Category) -> CategoryRead:
    """Convert a Category ORM object to CategoryRead, mapping children -> subcategories."""
    subcategories = [
        _category_to_read(child) for child in (cat.children or [])
    ]
    return CategoryRead(
        id=cat.id,
        name=cat.name,
        icon=cat.icon,
        color=cat.color,
        type=cat.type,
        budget_limit=cat.budget_limit,
        parent_id=cat.parent_id,
        tenant_id=cat.tenant_id,
        created_at=cat.created_at,
        updated_at=cat.updated_at,
        subcategories=subcategories,
    )


@router.get("", response_model=list[CategoryRead])
async def list_categories(
    type: str | None = Query(default=None, description="Filter by type: income or expense"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all categories for the current tenant."""
    query = (
        select(Category)
        .where(Category.tenant_id == current_user.tenant_id)
        .options(selectinload(Category.children))
    )
    if type:
        query = query.where(Category.type == type)
    # Only return top-level categories (parent_id is None)
    query = query.where(Category.parent_id.is_(None))
    result = await db.execute(query)
    categories = result.scalars().all()
    return [_category_to_read(c) for c in categories]


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new category (checks plan limit)."""
    await check_resource_limit(db, current_user.tenant_id, "categories", Category)

    category = Category(
        name=payload.name,
        icon=payload.icon,
        color=payload.color,
        type=payload.type,
        parent_id=payload.parent_id,
        budget_limit=payload.budget_limit,
        tenant_id=current_user.tenant_id,
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return _category_to_read(category)


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(
    category_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a category by ID with its subcategories."""
    result = await db.execute(
        select(Category)
        .where(Category.id == category_id, Category.tenant_id == current_user.tenant_id)
        .options(selectinload(Category.children))
    )
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return _category_to_read(category)


@router.put("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: UUID,
    payload: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a category."""
    result = await db.execute(
        select(Category)
        .where(Category.id == category_id, Category.tenant_id == current_user.tenant_id)
        .options(selectinload(Category.children))
    )
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)
    return _category_to_read(category)


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(
    category_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a category."""
    result = await db.execute(
        select(Category).where(
            Category.id == category_id, Category.tenant_id == current_user.tenant_id
        )
    )
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    await db.delete(category)
    await db.commit()
    return {"detail": "Category deleted"}
