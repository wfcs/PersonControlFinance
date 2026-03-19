from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.invoice import InvoiceCreate, InvoiceResponse, InvoiceUpdate
from app.services.invoice_service import (
    create_invoice,
    delete_invoice,
    get_invoice,
    list_invoices,
    update_invoice,
)

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.get("", response_model=list[InvoiceResponse])
async def list_all(
    account_id: Optional[UUID] = Query(default=None),
    status: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[InvoiceResponse]:
    invs = await list_invoices(
        current_user.tenant_id, session, account_id=account_id, invoice_status=status
    )
    return [InvoiceResponse.model_validate(i) for i in invs]


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_one(
    invoice_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> InvoiceResponse:
    inv = await get_invoice(invoice_id, current_user.tenant_id, session)
    return InvoiceResponse.model_validate(inv)


@router.post("", response_model=InvoiceResponse, status_code=201)
async def create(
    data: InvoiceCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> InvoiceResponse:
    inv = await create_invoice(data, current_user.tenant_id, session)
    return InvoiceResponse.model_validate(inv)


@router.patch("/{invoice_id}", response_model=InvoiceResponse)
async def update(
    invoice_id: UUID,
    data: InvoiceUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> InvoiceResponse:
    inv = await update_invoice(invoice_id, data, current_user.tenant_id, session)
    return InvoiceResponse.model_validate(inv)


@router.delete("/{invoice_id}", status_code=204)
async def delete(
    invoice_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    await delete_invoice(invoice_id, current_user.tenant_id, session)
