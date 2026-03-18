"""Service layer for transaction operations."""

from __future__ import annotations

import csv
import io
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.transaction import Transaction
from app.schemas.transaction import TransactionFilters


def build_transaction_query(
    tenant_id: UUID,
    filters: TransactionFilters,
):
    """Build a SQLAlchemy query with filters applied."""
    query = select(Transaction).where(Transaction.tenant_id == tenant_id)

    if filters.start_date is not None:
        query = query.where(Transaction.date >= filters.start_date)
    if filters.end_date is not None:
        query = query.where(Transaction.date <= filters.end_date)
    if filters.account_id is not None:
        query = query.where(Transaction.account_id == filters.account_id)
    if filters.category_id is not None:
        query = query.where(Transaction.category_id == filters.category_id)
    if filters.type is not None:
        query = query.where(Transaction.type == filters.type)
    if filters.min_amount is not None:
        query = query.where(Transaction.amount >= filters.min_amount)
    if filters.max_amount is not None:
        query = query.where(Transaction.amount <= filters.max_amount)
    if filters.search:
        query = query.where(Transaction.description.ilike(f"%{filters.search}%"))

    return query


async def get_transactions_paginated(
    db: AsyncSession,
    tenant_id: UUID,
    filters: TransactionFilters,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Transaction], int]:
    """Return paginated transactions with filters."""
    base_query = build_transaction_query(tenant_id, filters)

    # Count total
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Paginate
    offset = (page - 1) * page_size
    data_query = (
        base_query.order_by(Transaction.date.desc())
        .offset(offset)
        .limit(page_size)
        .options(selectinload(Transaction.category), selectinload(Transaction.account))
    )
    result = await db.execute(data_query)
    items = list(result.scalars().all())

    return items, total


async def export_transactions_csv(
    db: AsyncSession,
    tenant_id: UUID,
    filters: TransactionFilters,
) -> str:
    """Export filtered transactions as a CSV string."""
    query = build_transaction_query(tenant_id, filters).order_by(Transaction.date.desc())
    result = await db.execute(query)
    transactions = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "description", "amount", "type", "date",
        "account_id", "category_id", "is_recurring", "notes",
    ])

    for tx in transactions:
        writer.writerow([
            str(tx.id),
            tx.description,
            str(tx.amount),
            tx.type,
            tx.date.isoformat(),
            str(tx.account_id),
            str(tx.category_id) if tx.category_id else "",
            str(tx.is_recurring),
            tx.notes or "",
        ])

    return output.getvalue()
