from __future__ import annotations

import logging
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.recurrence import Recurrence
from app.models.transaction import Transaction

logger = logging.getLogger(__name__)


async def answer_question(
    question: str,
    tenant_id: UUID,
    session: AsyncSession,
) -> str:
    """Generate a financial insight answer based on user data.

    This is a rule-based engine. Future: integrate with Claude API for
    natural language understanding.
    """
    q = question.lower()

    # Total balance
    if any(k in q for k in ["saldo", "balance", "quanto tenho"]):
        result = await session.execute(
            select(func.coalesce(func.sum(Account.balance), Decimal("0"))).where(
                Account.tenant_id == tenant_id
            )
        )
        total = result.scalar()
        return f"Seu saldo total é R$ {total:,.2f}."

    # Monthly spending
    if any(k in q for k in ["gasto", "despesa", "gastei", "spending"]):
        from datetime import date
        today = date.today()
        first_day = today.replace(day=1)
        result = await session.execute(
            select(func.coalesce(func.sum(Transaction.amount), Decimal("0"))).where(
                Transaction.tenant_id == tenant_id,
                Transaction.type.in_(["expense", "despesa"]),
                Transaction.date >= first_day,
                Transaction.date <= today,
            )
        )
        total = result.scalar()
        return f"Seus gastos neste mês totalizam R$ {total:,.2f}."

    # Recurring expenses
    if any(k in q for k in ["recorr", "fixo", "recurring"]):
        result = await session.execute(
            select(func.coalesce(func.sum(Recurrence.amount), Decimal("0"))).where(
                Recurrence.tenant_id == tenant_id,
                Recurrence.is_active == True,  # noqa: E712
                Recurrence.type.in_(["expense", "despesa"]),
            )
        )
        total = result.scalar()
        return f"Suas despesas recorrentes ativas somam R$ {total:,.2f}/mês."

    # Account count
    if any(k in q for k in ["conta", "account", "quantas contas"]):
        result = await session.execute(
            select(func.count()).where(Account.tenant_id == tenant_id)
        )
        count = result.scalar()
        return f"Você possui {count} conta(s) cadastrada(s)."

    return (
        "Desculpe, ainda não consigo responder essa pergunta. "
        "Tente perguntar sobre seu saldo, gastos do mês, ou despesas recorrentes."
    )
