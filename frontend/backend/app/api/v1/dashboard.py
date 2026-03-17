from datetime import datetime, timezone

from fastapi import APIRouter, Query

from app.core.deps import AuthUser, DBSession
from app.services import transaction_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
async def summary(
    current_user: AuthUser,
    db: DBSession,
    year: int = Query(default_factory=lambda: datetime.now(timezone.utc).year),
    month: int = Query(default_factory=lambda: datetime.now(timezone.utc).month, ge=1, le=12),
) -> dict:
    """
    Retorna em uma única chamada:
    - Resumo do mês (receita, gasto, resultado)
    - Gastos por categoria
    - Últimas 10 transações
    """
    monthly = await transaction_service.get_monthly_summary(
        current_user.tenant_id, db, year, month
    )
    by_category = await transaction_service.get_spending_by_category(
        current_user.tenant_id, db, year, month
    )
    recent = await transaction_service.list_transactions(
        current_user.tenant_id, db, page=1, page_size=10
    )

    return {
        "period": {"year": year, "month": month},
        "summary": monthly,
        "spending_by_category": by_category,
        "recent_transactions": [t.model_dump() for t in recent.items],
    }


@router.get("/cash-flow")
async def cash_flow(
    current_user: AuthUser,
    db: DBSession,
    months: int = Query(3, ge=1, le=12),
) -> list[dict]:
    """Receita e gasto dos últimos N meses para o gráfico de fluxo de caixa."""
    now = datetime.now(timezone.utc)
    result = []
    for i in range(months - 1, -1, -1):
        m = now.month - i
        y = now.year
        while m <= 0:
            m += 12
            y -= 1
        data = await transaction_service.get_monthly_summary(current_user.tenant_id, db, y, m)
        result.append({"year": y, "month": m, **data})
    return result
