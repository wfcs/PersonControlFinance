from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionFilter, TransactionUpdate


async def list_transactions(
    tenant_id: UUID,
    session: AsyncSession,
    filters: TransactionFilter | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Transaction]:
    query = select(Transaction).where(Transaction.tenant_id == tenant_id)

    if filters:
        if filters.date_from:
            query = query.where(Transaction.date >= filters.date_from)
        if filters.date_to:
            query = query.where(Transaction.date <= filters.date_to)
        if filters.account_id:
            query = query.where(Transaction.account_id == filters.account_id)
        if filters.category_id:
            query = query.where(Transaction.category_id == filters.category_id)
        if filters.type:
            query = query.where(Transaction.type == filters.type)
        if filters.min_amount is not None:
            query = query.where(Transaction.amount >= filters.min_amount)
        if filters.max_amount is not None:
            query = query.where(Transaction.amount <= filters.max_amount)
        if filters.search:
            query = query.where(Transaction.description.ilike(f"%{filters.search}%"))

    query = query.order_by(Transaction.date.desc()).limit(limit).offset(offset)
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_transaction(
    transaction_id: UUID, tenant_id: UUID, session: AsyncSession
) -> Transaction:
    result = await session.execute(
        select(Transaction).where(
            Transaction.id == transaction_id, Transaction.tenant_id == tenant_id
        )
    )
    txn = result.scalar_one_or_none()
    if txn is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return txn


async def create_transaction(
    data: TransactionCreate, tenant_id: UUID, session: AsyncSession
) -> Transaction:
    txn = Transaction(**data.model_dump(), tenant_id=tenant_id)
    session.add(txn)
    await session.flush()
    return txn


async def update_transaction(
    transaction_id: UUID, data: TransactionUpdate, tenant_id: UUID, session: AsyncSession
) -> Transaction:
    txn = await get_transaction(transaction_id, tenant_id, session)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(txn, field, value)
    await session.flush()
    return txn


async def delete_transaction(
    transaction_id: UUID, tenant_id: UUID, session: AsyncSession
) -> None:
    txn = await get_transaction(transaction_id, tenant_id, session)
    await session.delete(txn)
    await session.flush()
