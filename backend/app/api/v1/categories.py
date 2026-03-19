from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services.category_service import (
    create_category,
    delete_category,
    get_category,
    list_categories,
    update_category,
)

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryResponse])
async def list_all(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[CategoryResponse]:
    cats = await list_categories(current_user.tenant_id, session)
    return [CategoryResponse.model_validate(c) for c in cats]


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_one(
    category_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> CategoryResponse:
    cat = await get_category(category_id, current_user.tenant_id, session)
    return CategoryResponse.model_validate(cat)


@router.post("", response_model=CategoryResponse, status_code=201)
async def create(
    data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> CategoryResponse:
    cat = await create_category(data, current_user.tenant_id, session)
    return CategoryResponse.model_validate(cat)


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update(
    category_id: UUID,
    data: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> CategoryResponse:
    cat = await update_category(category_id, data, current_user.tenant_id, session)
    return CategoryResponse.model_validate(cat)


@router.delete("/{category_id}", status_code=204)
async def delete(
    category_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    await delete_category(category_id, current_user.tenant_id, session)
