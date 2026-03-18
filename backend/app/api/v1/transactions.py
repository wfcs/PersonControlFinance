"""Transaction CRUD endpoints with filters, pagination, and CSV export."""

from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user, get_db
from app.core.plan_guard import require_feature
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import (
    PaginatedResponse,
    TransactionCreate,
    TransactionFilters,
    TransactionRead,
    TransactionUpdate,
)
from app.services.categorization_service import categorize_transaction
from app.services.transaction_service import export_transactions_csv, get_transactions_paginated

router = APIRouter(prefix="/transactions", tags=["transactions"])


def _tx_to_read(tx: Transaction) -> TransactionRead:
    """Convert a Transaction ORM object to TransactionRead with related names."""
    # Access eagerly loaded relationships safely
    category_name = None
    account_name = None
    try:
        if tx.category:
            category_name = tx.category.name
    except Exception:
        pass
    try:
        if tx.account:
            account_name = tx.account.name
    except Exception:
        pass

    return TransactionRead(
        id=tx.id,
        description=tx.description,
        amount=tx.amount,
        type=tx.type,
        date=tx.date,
        is_recurring=tx.is_recurring,
        notes=tx.notes,
        account_id=tx.account_id,
        category_id=tx.category_id,
        tenant_id=tx.tenant_id,
        created_at=tx.created_at,
        updated_at=tx.updated_at,
        category_name=category_name,
        account_name=account_name,
    )


async def _load_transaction(db: AsyncSession, transaction_id: UUID, tenant_id: UUID) -> Transaction | None:
    """Load a transaction with its relationships eagerly."""
    result = await db.execute(
        select(Transaction)
        .where(Transaction.id == transaction_id, Transaction.tenant_id == tenant_id)
        .options(selectinload(Transaction.category), selectinload(Transaction.account))
    )
    return result.scalar_one_or_none()


@router.get("", response_model=PaginatedResponse[TransactionRead])
async def list_transactions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    account_id: Optional[UUID] = None,
    category_id: Optional[UUID] = None,
    type: Optional[str] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List transactions with filters and pagination."""
    filters = TransactionFilters(
        start_date=start_date,
        end_date=end_date,
        account_id=account_id,
        category_id=category_id,
        type=type,
        min_amount=min_amount,
        max_amount=max_amount,
        search=search,
    )
    items, total = await get_transactions_paginated(
        db, current_user.tenant_id, filters, page, page_size
    )
    return PaginatedResponse(
        items=[_tx_to_read(tx) for tx in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    payload: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new transaction (with auto-categorization if no category provided)."""
    # Auto-categorize if no category_id
    category_id = payload.category_id
    if category_id is None:
        auto_cat_id = await categorize_transaction(
            payload.description,
            str(current_user.tenant_id),
            db,
        )
        if auto_cat_id:
            category_id = UUID(auto_cat_id)

    transaction = Transaction(
        description=payload.description,
        amount=payload.amount,
        type=payload.type,
        date=payload.date,
        account_id=payload.account_id,
        category_id=category_id,
        is_recurring=payload.is_recurring,
        notes=payload.notes,
        tenant_id=current_user.tenant_id,
    )
    db.add(transaction)
    await db.commit()

    # Reload with relationships
    loaded = await _load_transaction(db, transaction.id, current_user.tenant_id)
    return _tx_to_read(loaded)


@router.get("/export/csv")
async def export_csv(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    account_id: Optional[UUID] = None,
    category_id: Optional[UUID] = None,
    type: Optional[str] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _feature: None = Depends(require_feature("export_csv")),
):
    """Export filtered transactions as CSV (Pro+ plan required)."""
    filters = TransactionFilters(
        start_date=start_date,
        end_date=end_date,
        account_id=account_id,
        category_id=category_id,
        type=type,
        min_amount=min_amount,
        max_amount=max_amount,
        search=search,
    )
    csv_content = await export_transactions_csv(db, current_user.tenant_id, filters)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"},
    )


@router.get("/{transaction_id}", response_model=TransactionRead)
async def get_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a transaction by ID."""
    tx = await _load_transaction(db, transaction_id, current_user.tenant_id)
    if tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return _tx_to_read(tx)


@router.put("/{transaction_id}", response_model=TransactionRead)
async def update_transaction(
    transaction_id: UUID,
    payload: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a transaction."""
    tx = await _load_transaction(db, transaction_id, current_user.tenant_id)
    if tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tx, field, value)

    await db.commit()
    loaded = await _load_transaction(db, transaction_id, current_user.tenant_id)
    return _tx_to_read(loaded)


@router.delete("/{transaction_id}", status_code=status.HTTP_200_OK)
async def delete_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a transaction."""
    result = await db.execute(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.tenant_id == current_user.tenant_id,
        )
    )
    tx = result.scalar_one_or_none()
    if tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    await db.delete(tx)
    await db.commit()
    return {"detail": "Transaction deleted"}
