"""Motor de detecção de recorrências e parcelas."""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recurrence import Recurrence
from app.models.transaction import Transaction
from app.schemas.recurrence import RecurrenceUpdate


async def list_recurrences(tenant_id: UUID, db: AsyncSession) -> list[Recurrence]:
    result = await db.scalars(
        select(Recurrence)
        .where(Recurrence.tenant_id == tenant_id)
        .order_by(Recurrence.is_active.desc(), Recurrence.next_due_date.asc())
    )
    return list(result.all())


async def get_recurrence(rec_id: UUID, tenant_id: UUID, db: AsyncSession) -> Recurrence:
    rec = await db.scalar(
        select(Recurrence).where(Recurrence.id == rec_id, Recurrence.tenant_id == tenant_id)
    )
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recorrência não encontrada")
    return rec


async def update_recurrence(
    rec_id: UUID, data: RecurrenceUpdate, tenant_id: UUID, db: AsyncSession
) -> Recurrence:
    rec = await get_recurrence(rec_id, tenant_id, db)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(rec, field, value)
    await db.flush()
    await db.refresh(rec)
    return rec


async def detect_recurrences(tenant_id: UUID, db: AsyncSession) -> list[Recurrence]:
    """Analisa histórico de transações e detecta parcelas + contas fixas."""
    recurrences: list[Recurrence] = []
    recurrences.extend(await _detect_installments(tenant_id, db))
    recurrences.extend(await _detect_fixed_recurring(tenant_id, db))
    await db.flush()
    return recurrences


# ── Detecção de parcelas ─────────────────────────────────────────────────────


async def _detect_installments(tenant_id: UUID, db: AsyncSession) -> list[Recurrence]:
    """Agrupa transações com installment_total preenchido por descrição normalizada."""
    result = await db.scalars(
        select(Transaction)
        .where(
            Transaction.tenant_id == tenant_id,
            Transaction.installment_total.isnot(None),
            Transaction.recurrence_id.is_(None),
        )
        .order_by(Transaction.description, Transaction.installment_number)
    )
    transactions = list(result.all())

    groups: dict[tuple, list[Transaction]] = defaultdict(list)
    for tx in transactions:
        key = (_normalize_desc(tx.description), tx.installment_total, _round_amount(tx.amount))
        groups[key].append(tx)

    recurrences: list[Recurrence] = []
    for (desc, total, amount), txs in groups.items():
        if len(txs) < 2:
            continue

        max_inst = max(tx.installment_number or 0 for tx in txs)
        last_date = max(tx.date for tx in txs)
        still_active = total is not None and max_inst < total

        rec = Recurrence(
            tenant_id=tenant_id,
            description=desc,
            amount=abs(amount),
            frequency="installment",
            total_installments=total,
            current_installment=max_inst,
            next_due_date=last_date.date() + timedelta(days=30) if still_active else None,
            is_active=still_active,
        )
        db.add(rec)
        await db.flush()

        for tx in txs:
            tx.recurrence_id = rec.id

        recurrences.append(rec)

    return recurrences


# ── Detecção de contas fixas ─────────────────────────────────────────────────


async def _detect_fixed_recurring(tenant_id: UUID, db: AsyncSession) -> list[Recurrence]:
    """
    Detecta despesas que se repetem mensalmente (3+ ocorrências,
    variação de valor < 10%, intervalo médio entre 20 e 40 dias).
    """
    six_months_ago = date.today() - timedelta(days=180)
    result = await db.scalars(
        select(Transaction)
        .where(
            Transaction.tenant_id == tenant_id,
            Transaction.amount < 0,
            Transaction.date >= six_months_ago,
            Transaction.recurrence_id.is_(None),
        )
        .order_by(Transaction.description, Transaction.date)
    )
    transactions = list(result.all())

    groups: dict[str, list[Transaction]] = defaultdict(list)
    for tx in transactions:
        key = _normalize_desc(tx.description)
        groups[key].append(tx)

    recurrences: list[Recurrence] = []
    for desc, txs in groups.items():
        if len(txs) < 3:
            continue

        amounts = [abs(tx.amount) for tx in txs]
        avg_amount = sum(amounts, Decimal("0")) / len(amounts)
        if avg_amount == 0:
            continue
        if any(abs(a - avg_amount) / avg_amount > Decimal("0.1") for a in amounts):
            continue

        dates = sorted(tx.date for tx in txs)
        intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
        avg_interval = sum(intervals) / len(intervals)
        if not (20 <= avg_interval <= 40):
            continue

        last_date = max(tx.date for tx in txs)
        next_due = last_date.date() + timedelta(days=int(avg_interval))

        rec = Recurrence(
            tenant_id=tenant_id,
            description=desc,
            amount=avg_amount,
            frequency="monthly",
            next_due_date=next_due,
            is_active=True,
        )
        db.add(rec)
        await db.flush()

        for tx in txs:
            tx.recurrence_id = rec.id

        recurrences.append(rec)

    return recurrences


# ── Helpers ──────────────────────────────────────────────────────────────────


def _normalize_desc(desc: str) -> str:
    """Normaliza descrição removendo datas, números de parcela, espaços extras."""
    desc = desc.upper().strip()
    desc = re.sub(r"\d{1,2}/\d{1,2}", "", desc)
    desc = re.sub(r"PARC\s*\d+", "", desc)
    desc = re.sub(r"\s+", " ", desc).strip()
    return desc


def _round_amount(amount: Decimal) -> Decimal:
    return Decimal(str(round(abs(amount))))
