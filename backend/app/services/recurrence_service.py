from __future__ import annotations

import re
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from dateutil.relativedelta import relativedelta
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recurrence import Recurrence
from app.models.transaction import Transaction
from app.schemas.recurrence import RecurrenceCreate, RecurrenceUpdate


async def list_recurrences(
    tenant_id: UUID, session: AsyncSession, active_only: bool = True
) -> list[Recurrence]:
    query = select(Recurrence).where(Recurrence.tenant_id == tenant_id)
    if active_only:
        query = query.where(Recurrence.is_active == True)  # noqa: E712
    query = query.order_by(Recurrence.next_due_date)
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_recurrence(
    recurrence_id: UUID, tenant_id: UUID, session: AsyncSession
) -> Recurrence:
    result = await session.execute(
        select(Recurrence).where(
            Recurrence.id == recurrence_id, Recurrence.tenant_id == tenant_id
        )
    )
    rec = result.scalar_one_or_none()
    if rec is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurrence not found")
    return rec


async def create_recurrence(
    data: RecurrenceCreate, tenant_id: UUID, session: AsyncSession
) -> Recurrence:
    rec = Recurrence(**data.model_dump(), tenant_id=tenant_id)
    session.add(rec)
    await session.flush()
    return rec


async def update_recurrence(
    recurrence_id: UUID, data: RecurrenceUpdate, tenant_id: UUID, session: AsyncSession
) -> Recurrence:
    rec = await get_recurrence(recurrence_id, tenant_id, session)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(rec, field, value)
    await session.flush()
    return rec


async def delete_recurrence(
    recurrence_id: UUID, tenant_id: UUID, session: AsyncSession
) -> None:
    rec = await get_recurrence(recurrence_id, tenant_id, session)
    await session.delete(rec)
    await session.flush()


def _advance_date(current: date, frequency: str) -> date:
    """Calculate next due date based on frequency."""
    freq = frequency.lower()
    if freq in ("daily", "diário", "diaria"):
        return current + timedelta(days=1)
    if freq in ("weekly", "semanal"):
        return current + timedelta(weeks=1)
    if freq in ("biweekly", "quinzenal"):
        return current + timedelta(weeks=2)
    if freq in ("monthly", "mensal"):
        return current + relativedelta(months=1)
    if freq in ("quarterly", "trimestral"):
        return current + relativedelta(months=3)
    if freq in ("yearly", "anual"):
        return current + relativedelta(years=1)
    # Default: monthly
    return current + relativedelta(months=1)


async def process_due_recurrences(
    tenant_id: UUID, session: AsyncSession, reference_date: date | None = None
) -> list[Transaction]:
    """Generate transactions for all recurrences due on or before reference_date."""
    if reference_date is None:
        reference_date = date.today()

    result = await session.execute(
        select(Recurrence).where(
            Recurrence.tenant_id == tenant_id,
            Recurrence.is_active == True,  # noqa: E712
            Recurrence.next_due_date <= reference_date,
        )
    )
    due_recurrences = list(result.scalars().all())
    created_transactions: list[Transaction] = []

    for rec in due_recurrences:
        txn = Transaction(
            description=f"[Recorrência] {rec.description}",
            amount=rec.amount,
            type=rec.type,
            date=rec.next_due_date,
            account_id=rec.account_id,
            category_id=rec.category_id,
            tenant_id=tenant_id,
            is_recurring=True,
        )
        session.add(txn)
        created_transactions.append(txn)
        rec.next_due_date = _advance_date(rec.next_due_date, rec.frequency)

    await session.flush()
    return created_transactions


def _normalize_desc(desc: str) -> str:
    """Normalize description for matching: lowercase, strip dates, strip 'PARC N/M'."""
    s = desc.lower().strip()
    s = re.sub(r"\d{2}/\d{2}/\d{4}", "", s)
    s = re.sub(r"\d{2}/\d{2}", "", s)
    s = re.sub(r"parc\s*\d+/\d+", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s+", " ", s).strip()
    return s


async def detect_recurrences(
    tenant_id: UUID, session: AsyncSession, months: int = 6
) -> list[Recurrence]:
    """Analyze last N months of transactions to detect recurring patterns."""
    cutoff = date.today() - timedelta(days=months * 30)
    result = await session.execute(
        select(Transaction)
        .where(Transaction.tenant_id == tenant_id, Transaction.date >= cutoff)
        .order_by(Transaction.date)
    )
    transactions = list(result.scalars().all())

    groups: dict[str, list[Transaction]] = defaultdict(list)
    for txn in transactions:
        key = _normalize_desc(txn.description)
        groups[key].append(txn)

    detected: list[Recurrence] = []

    for key, txns in groups.items():
        if len(txns) < 3:
            continue

        amounts = [float(t.amount) for t in txns]
        avg_amount = sum(amounts) / len(amounts)
        if avg_amount == 0:
            continue
        max_var = max(abs(a - avg_amount) / avg_amount for a in amounts)
        if max_var > 0.10:
            continue

        dates = sorted(t.date for t in txns)
        intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
        avg_interval = sum(intervals) / len(intervals)

        if 20 <= avg_interval <= 40:
            frequency = "mensal"
        elif 5 <= avg_interval <= 10:
            frequency = "semanal"
        elif 12 <= avg_interval <= 19:
            frequency = "quinzenal"
        else:
            continue

        existing = await session.execute(
            select(Recurrence).where(
                Recurrence.tenant_id == tenant_id,
                func.lower(Recurrence.description) == key,
                Recurrence.is_active == True,  # noqa: E712
            )
        )
        if existing.scalar_one_or_none() is not None:
            continue

        last_txn = txns[-1]
        next_due = _advance_date(last_txn.date, frequency)

        rec = Recurrence(
            description=last_txn.description,
            amount=Decimal(str(round(avg_amount, 2))),
            type=last_txn.type,
            frequency=frequency,
            next_due_date=next_due,
            account_id=last_txn.account_id,
            category_id=last_txn.category_id,
            tenant_id=tenant_id,
            is_active=True,
        )
        session.add(rec)
        detected.append(rec)

    if detected:
        await session.flush()

    return detected
