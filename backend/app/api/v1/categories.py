from uuid import UUID

from fastapi import APIRouter, status

from app.core.deps import AuthUser, DBSession
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.services import category_service

router = APIRouter(prefix="/categories", tags=["Categorias"])


@router.get("/", response_model=list[CategoryOut])
async def list_categories(current_user: AuthUser, db: DBSession) -> list[CategoryOut]:
    """Retorna categorias com subcategorias aninhadas."""
    rows = await category_service.list_categories(current_user.tenant_id, db)
    return [CategoryOut.model_validate(r) for r in rows]


@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate, current_user: AuthUser, db: DBSession
) -> CategoryOut:
    cat = await category_service.create_category(data, current_user.tenant_id, db)
    return CategoryOut.model_validate(cat)


@router.patch("/{cat_id}", response_model=CategoryOut)
async def update_category(
    cat_id: UUID, data: CategoryUpdate, current_user: AuthUser, db: DBSession
) -> CategoryOut:
    cat = await category_service.update_category(cat_id, data, current_user.tenant_id, db)
    return CategoryOut.model_validate(cat)


@router.delete("/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(cat_id: UUID, current_user: AuthUser, db: DBSession) -> None:
    await category_service.delete_category(cat_id, current_user.tenant_id, db)
