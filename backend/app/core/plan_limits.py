"""Definição de planos e seus limites de features."""

from __future__ import annotations

from enum import Enum


class Plan(str, Enum):
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"


PLAN_LIMITS: dict[str, dict] = {
    Plan.FREE: {
        "max_accounts": 2,
        "max_manual_transactions_per_month": 100,
        "open_finance": False,
        "projections": False,
        "csv_export": False,
        "ai_assistant": False,
        "patrimony": False,
    },
    Plan.PRO: {
        "max_accounts": 10,
        "max_manual_transactions_per_month": 1000,
        "open_finance": True,
        "projections": True,
        "csv_export": True,
        "ai_assistant": False,
        "patrimony": True,
    },
    Plan.PREMIUM: {
        "max_accounts": -1,  # ilimitado
        "max_manual_transactions_per_month": -1,
        "open_finance": True,
        "projections": True,
        "csv_export": True,
        "ai_assistant": True,
        "patrimony": True,
    },
}
