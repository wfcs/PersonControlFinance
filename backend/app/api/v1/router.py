from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.accounts import router as accounts_router
from app.api.v1.admin import router as admin_router
from app.api.v1.ai_assistant import router as ai_router
from app.api.v1.audit import router as audit_router
from app.api.v1.auth import router as auth_router
from app.api.v1.billing import router as billing_router
from app.api.v1.cashflow import router as cashflow_router
from app.api.v1.categories import router as categories_router
from app.api.v1.goals import router as goals_router
from app.api.v1.invoices import router as invoices_router
from app.api.v1.networth import router as networth_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.open_finance import router as open_finance_router
from app.api.v1.projection import router as projection_router
from app.api.v1.recurrences import router as recurrences_router
from app.api.v1.transactions import router as transactions_router
from app.api.v1.webhooks import router as webhooks_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(accounts_router)
api_router.include_router(transactions_router)
api_router.include_router(categories_router)
api_router.include_router(goals_router)
api_router.include_router(recurrences_router)
api_router.include_router(cashflow_router)
api_router.include_router(projection_router)
api_router.include_router(networth_router)
api_router.include_router(invoices_router)
api_router.include_router(notifications_router)
api_router.include_router(ai_router)
api_router.include_router(admin_router)
api_router.include_router(open_finance_router)
api_router.include_router(audit_router)
api_router.include_router(billing_router)
api_router.include_router(webhooks_router)
