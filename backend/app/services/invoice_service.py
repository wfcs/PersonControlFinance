from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invoice import Invoice
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate


async def list_invoices(
    tenant_id: UUID,
    session: AsyncSession,
    account_id: UUID | None = None,
    invoice_status: str | None = None,
) -> list[Invoice]:
    query = select(Invoice).where(Invoice.tenant_id == tenant_id)
    if account_id:
        query = query.where(Invoice.credit_card_account_id == account_id)
    if invoice_status:
        query = query.where(Invoice.status == invoice_status)
    query = query.order_by(Invoice.due_date.desc())
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_invoice(
    invoice_id: UUID, tenant_id: UUID, session: AsyncSession
) -> Invoice:
    result = await session.execute(
        select(Invoice).where(
            Invoice.id == invoice_id, Invoice.tenant_id == tenant_id
        )
    )
    inv = result.scalar_one_or_none()
    if inv is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return inv


async def create_invoice(
    data: InvoiceCreate, tenant_id: UUID, session: AsyncSession
) -> Invoice:
    inv = Invoice(**data.model_dump(), tenant_id=tenant_id)
    session.add(inv)
    await session.flush()
    return inv


async def update_invoice(
    invoice_id: UUID, data: InvoiceUpdate, tenant_id: UUID, session: AsyncSession
) -> Invoice:
    inv = await get_invoice(invoice_id, tenant_id, session)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(inv, field, value)
    await session.flush()
    return inv


async def delete_invoice(
    invoice_id: UUID, tenant_id: UUID, session: AsyncSession
) -> None:
    inv = await get_invoice(invoice_id, tenant_id, session)
    await session.delete(inv)
    await session.flush()
