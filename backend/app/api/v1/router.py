from fastapi import APIRouter

from app.api.v1 import (
    admin,
    auth,
    accounts,
    billing,
    bills,
    categories,
    dashboard,
    notifications,
    open_finance,
    patrimony,
    projections,
    recurrences,
    transactions,
    webhooks,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(accounts.router)
api_router.include_router(transactions.router)
api_router.include_router(categories.router)
api_router.include_router(dashboard.router)
api_router.include_router(open_finance.router)
api_router.include_router(webhooks.router)
api_router.include_router(recurrences.router)
api_router.include_router(bills.router)
api_router.include_router(projections.router)
api_router.include_router(patrimony.router)
api_router.include_router(billing.router)
api_router.include_router(notifications.router)
api_router.include_router(admin.router)
