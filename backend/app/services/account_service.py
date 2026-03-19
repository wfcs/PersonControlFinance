from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.schemas.account import AccountCreate, AccountUpdate


async def list_accounts(tenant_id: UUID, session: AsyncSession) -> list[Account]:
    result = await session.execute(
        select(Account).where(Account.tenant_id == tenant_id).order_by(Account.name)
    )
    return list(result.scalars().all())


async def get_account(account_id: UUID, tenant_id: UUID, session: AsyncSession) -> Account:
    result = await session.execute(
        select(Account).where(Account.id == account_id, Account.tenant_id == tenant_id)
    )
    account = result.scalar_one_or_none()
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return account


async def create_account(data: AccountCreate, tenant_id: UUID, session: AsyncSession) -> Account:
    account = Account(**data.model_dump(), tenant_id=tenant_id)
    session.add(account)
    await session.flush()
    return account


async def update_account(
    account_id: UUID, data: AccountUpdate, tenant_id: UUID, session: AsyncSession
) -> Account:
    account = await get_account(account_id, tenant_id, session)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(account, field, value)
    await session.flush()
    return account


async def delete_account(account_id: UUID, tenant_id: UUID, session: AsyncSession) -> None:
    account = await get_account(account_id, tenant_id, session)
    await session.delete(account)
    await session.flush()
