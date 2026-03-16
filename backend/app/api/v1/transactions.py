from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Query, status
from fastapi.responses import StreamingResponse

from app.core.deps import AuthUser, DBSession
from app.schemas.transaction import (
    TransactionCreate,
    TransactionListResponse,
    TransactionOut,
    TransactionUpdate,
)
from app.services import transaction_service
import csv
import io

router = APIRouter(prefix="/transactions", tags=["Transações"])


@router.get("/", response_model=TransactionListResponse)
async def list_transactions(
    current_user: AuthUser,
    db: DBSession,
    account_id: UUID | None = Query(None),
    category_id: UUID | None = Query(None),
    type: str | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=100),
) -> TransactionListResponse:
    """Lista transações com filtros e paginação."""
    return await transaction_service.list_transactions(
        current_user.tenant_id,
        db,
        account_id=account_id,
        category_id=category_id,
        type=type,
        date_from=date_from,
        date_to=date_to,
        search=search,
        page=page,
        page_size=page_size,
    )


@router.post("/", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    data: TransactionCreate, current_user: AuthUser, db: DBSession
) -> TransactionOut:
    tx = await transaction_service.create_transaction(data, current_user.tenant_id, db)
    return TransactionOut.model_validate(tx)


@router.get("/summary")
async def monthly_summary(
    current_user: AuthUser,
    db: DBSession,
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
) -> dict:
    """Receita, gasto e resultado do mês."""
    return await transaction_service.get_monthly_summary(current_user.tenant_id, db, year, month)


@router.get("/by-category")
async def spending_by_category(
    current_user: AuthUser,
    db: DBSession,
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
) -> list[dict]:
    """Gastos agrupados por categoria do mês."""
    return await transaction_service.get_spending_by_category(current_user.tenant_id, db, year, month)


@router.get("/export/csv")
async def export_csv(
    current_user: AuthUser,
    db: DBSession,
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
) -> StreamingResponse:
    """Exporta transações em CSV."""
    result = await transaction_service.list_transactions(
        current_user.tenant_id,
        db,
        date_from=date_from,
        date_to=date_to,
        page=1,
        page_size=10_000,
    )
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["id", "date", "description", "amount", "type", "category_id", "account_id", "notes"],
    )
    writer.writeheader()
    for tx in result.items:
        writer.writerow(tx.model_dump(include=set(writer.fieldnames)))

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transacoes.csv"},
    )


@router.get("/{tx_id}", response_model=TransactionOut)
async def get_transaction(tx_id: UUID, current_user: AuthUser, db: DBSession) -> TransactionOut:
    tx = await transaction_service.get_transaction(tx_id, current_user.tenant_id, db)
    return TransactionOut.model_validate(tx)


@router.patch("/{tx_id}", response_model=TransactionOut)
async def update_transaction(
    tx_id: UUID, data: TransactionUpdate, current_user: AuthUser, db: DBSession
) -> TransactionOut:
    tx = await transaction_service.update_transaction(tx_id, data, current_user.tenant_id, db)
    return TransactionOut.model_validate(tx)


@router.delete("/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(tx_id: UUID, current_user: AuthUser, db: DBSession) -> None:
    await transaction_service.delete_transaction(tx_id, current_user.tenant_id, db)
