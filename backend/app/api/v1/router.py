from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.accounts import router as accounts_router
from app.api.v1.auth import router as auth_router
from app.api.v1.categories import router as categories_router
from app.api.v1.goals import router as goals_router
from app.api.v1.transactions import router as transactions_router
from app.api.v1.webhooks import router as webhooks_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(accounts_router)
api_router.include_router(transactions_router)
api_router.include_router(categories_router)
api_router.include_router(goals_router)
api_router.include_router(webhooks_router)
