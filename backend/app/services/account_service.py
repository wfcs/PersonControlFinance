from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.schemas.account import AccountCreate, AccountUpdate


async def list_accounts(tenant_id: UUID, db: AsyncSession) -> list[Account]:
    rows = (
        await db.scalars(
            select(Account)
            .where(Account.tenant_id == tenant_id, Account.is_active.is_(True))
            .order_by(Account.institution_name, Account.name)
        )
    ).all()
    return list(rows)


async def get_account(account_id: UUID, tenant_id: UUID, db: AsyncSession) -> Account:
    acc = await db.scalar(
        select(Account).where(Account.id == account_id, Account.tenant_id == tenant_id)
    )
    if not acc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conta não encontrada")
    return acc


async def create_account(data: AccountCreate, tenant_id: UUID, db: AsyncSession) -> Account:
    acc = Account(**data.model_dump(), tenant_id=tenant_id)
    db.add(acc)
    await db.flush()
    await db.refresh(acc)
    return acc


async def update_account(
    account_id: UUID, data: AccountUpdate, tenant_id: UUID, db: AsyncSession
) -> Account:
    acc = await get_account(account_id, tenant_id, db)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(acc, field, value)
    await db.flush()
    await db.refresh(acc)
    return acc


async def delete_account(account_id: UUID, tenant_id: UUID, db: AsyncSession) -> None:
    """Soft delete — desativa a conta sem apagar do banco."""
    acc = await get_account(account_id, tenant_id, db)
    acc.is_active = False
    await db.flush()
