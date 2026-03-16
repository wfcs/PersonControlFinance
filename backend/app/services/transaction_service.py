from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction
from app.schemas.transaction import (
    TransactionCreate,
    TransactionListResponse,
    TransactionOut,
    TransactionUpdate,
)


async def list_transactions(
    tenant_id: UUID,
    db: AsyncSession,
    *,
    account_id: UUID | None = None,
    category_id: UUID | None = None,
    type: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 30,
) -> TransactionListResponse:
    filters = [Transaction.tenant_id == tenant_id]

    if account_id:
        filters.append(Transaction.account_id == account_id)
    if category_id:
        filters.append(Transaction.category_id == category_id)
    if type:
        filters.append(Transaction.type == type)
    if date_from:
        filters.append(Transaction.date >= date_from)
    if date_to:
        filters.append(Transaction.date <= date_to)
    if search:
        filters.append(Transaction.description.ilike(f"%{search}%"))

    total_q = select(func.count()).select_from(Transaction).where(and_(*filters))
    total = await db.scalar(total_q) or 0

    offset = (page - 1) * page_size
    q = (
        select(Transaction)
        .where(and_(*filters))
        .order_by(Transaction.date.desc())
        .offset(offset)
        .limit(page_size)
    )
    rows = (await db.scalars(q)).all()

    return TransactionListResponse(
        items=[TransactionOut.model_validate(r) for r in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


async def get_transaction(tx_id: UUID, tenant_id: UUID, db: AsyncSession) -> Transaction:
    tx = await db.scalar(
        select(Transaction).where(Transaction.id == tx_id, Transaction.tenant_id == tenant_id)
    )
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transação não encontrada")
    return tx


async def create_transaction(data: TransactionCreate, tenant_id: UUID, db: AsyncSession) -> Transaction:
    tx = Transaction(**data.model_dump(), tenant_id=tenant_id)
    db.add(tx)
    await db.flush()
    await db.refresh(tx)
    return tx


async def update_transaction(
    tx_id: UUID, data: TransactionUpdate, tenant_id: UUID, db: AsyncSession
) -> Transaction:
    tx = await get_transaction(tx_id, tenant_id, db)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(tx, field, value)
    await db.flush()
    await db.refresh(tx)
    return tx


async def delete_transaction(tx_id: UUID, tenant_id: UUID, db: AsyncSession) -> None:
    tx = await get_transaction(tx_id, tenant_id, db)
    await db.delete(tx)


# ── Agregações para o dashboard ───────────────────────────────────────────────

async def get_monthly_summary(
    tenant_id: UUID, db: AsyncSession, year: int, month: int
) -> dict:
    """Receita, gasto e resultado para o mês informado."""
    date_from = datetime(year, month, 1)
    # último dia do mês
    if month == 12:
        date_to = datetime(year + 1, 1, 1)
    else:
        date_to = datetime(year, month + 1, 1)

    q = select(
        func.sum(
            Transaction.amount.filter(Transaction.amount > 0)  # type: ignore[attr-defined]
        ).label("receita"),
        func.sum(
            Transaction.amount.filter(Transaction.amount < 0)  # type: ignore[attr-defined]
        ).label("gasto"),
    ).where(
        Transaction.tenant_id == tenant_id,
        Transaction.date >= date_from,
        Transaction.date < date_to,
        Transaction.is_excluded.is_(False),
    )
    row = (await db.execute(q)).one()
    receita = Decimal(row.receita or 0)
    gasto = abs(Decimal(row.gasto or 0))
    return {
        "receita": receita,
        "gasto": gasto,
        "resultado": receita - gasto,
    }


async def get_spending_by_category(
    tenant_id: UUID, db: AsyncSession, year: int, month: int
) -> list[dict]:
    """Gastos agrupados por categoria para o mês."""
    date_from = datetime(year, month, 1)
    date_to = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)

    q = (
        select(
            Transaction.category_id,
            func.sum(Transaction.amount).label("total"),
        )
        .where(
            Transaction.tenant_id == tenant_id,
            Transaction.date >= date_from,
            Transaction.date < date_to,
            Transaction.amount < 0,
            Transaction.is_excluded.is_(False),
        )
        .group_by(Transaction.category_id)
        .order_by(func.sum(Transaction.amount))
    )
    rows = (await db.execute(q)).all()
    return [{"category_id": r.category_id, "total": abs(Decimal(r.total))} for r in rows]
