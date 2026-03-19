from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionFilter,
    TransactionResponse,
    TransactionUpdate,
)
from app.services.transaction_service import (
    create_transaction,
    delete_transaction,
    get_transaction,
    list_transactions,
    update_transaction,
)

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=list[TransactionResponse])
async def list_all(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    account_id: Optional[UUID] = Query(None),
    category_id: Optional[UUID] = Query(None),
    type: Optional[str] = Query(None),
    min_amount: Optional[Decimal] = Query(None),
    max_amount: Optional[Decimal] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[TransactionResponse]:
    filters = TransactionFilter(
        date_from=date_from,
        date_to=date_to,
        account_id=account_id,
        category_id=category_id,
        type=type,
        min_amount=min_amount,
        max_amount=max_amount,
        search=search,
    )
    txns = await list_transactions(current_user.tenant_id, session, filters, limit, offset)
    return [TransactionResponse.model_validate(t) for t in txns]


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_one(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TransactionResponse:
    txn = await get_transaction(transaction_id, current_user.tenant_id, session)
    return TransactionResponse.model_validate(txn)


@router.post("", response_model=TransactionResponse, status_code=201)
async def create(
    data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TransactionResponse:
    txn = await create_transaction(data, current_user.tenant_id, session)
    return TransactionResponse.model_validate(txn)


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update(
    transaction_id: UUID,
    data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TransactionResponse:
    txn = await update_transaction(transaction_id, data, current_user.tenant_id, session)
    return TransactionResponse.model_validate(txn)


@router.delete("/{transaction_id}", status_code=204)
async def delete(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    await delete_transaction(transaction_id, current_user.tenant_id, session)
