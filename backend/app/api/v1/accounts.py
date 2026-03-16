from uuid import UUID

from fastapi import APIRouter, status

from app.core.deps import AuthUser, DBSession
from app.schemas.account import AccountCreate, AccountOut, AccountUpdate
from app.services import account_service

router = APIRouter(prefix="/accounts", tags=["Contas"])


@router.get("/", response_model=list[AccountOut])
async def list_accounts(current_user: AuthUser, db: DBSession) -> list[AccountOut]:
    """Lista todas as contas ativas do tenant."""
    rows = await account_service.list_accounts(current_user.tenant_id, db)
    return [AccountOut.model_validate(r) for r in rows]


@router.post("/", response_model=AccountOut, status_code=status.HTTP_201_CREATED)
async def create_account(
    data: AccountCreate, current_user: AuthUser, db: DBSession
) -> AccountOut:
    """Cria conta manual (sem Open Finance)."""
    acc = await account_service.create_account(data, current_user.tenant_id, db)
    return AccountOut.model_validate(acc)


@router.get("/{account_id}", response_model=AccountOut)
async def get_account(account_id: UUID, current_user: AuthUser, db: DBSession) -> AccountOut:
    acc = await account_service.get_account(account_id, current_user.tenant_id, db)
    return AccountOut.model_validate(acc)


@router.patch("/{account_id}", response_model=AccountOut)
async def update_account(
    account_id: UUID, data: AccountUpdate, current_user: AuthUser, db: DBSession
) -> AccountOut:
    acc = await account_service.update_account(account_id, data, current_user.tenant_id, db)
    return AccountOut.model_validate(acc)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: UUID, current_user: AuthUser, db: DBSession) -> None:
    """Soft delete — desativa a conta."""
    await account_service.delete_account(account_id, current_user.tenant_id, db)
