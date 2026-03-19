from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PlanLimits:
    name: str
    max_connections: int
    max_accounts: int
    max_transactions_month: int
    features: list[str] = field(default_factory=list)


PLANS: dict[str, PlanLimits] = {
    "free": PlanLimits(
        name="free",
        max_connections=1,
        max_accounts=2,
        max_transactions_month=100,
        features=["basic_dashboard"],
    ),
    "pro": PlanLimits(
        name="pro",
        max_connections=3,
        max_accounts=10,
        max_transactions_month=5000,
        features=[
            "basic_dashboard",
            "reports",
            "export_csv",
            "recurrences",
        ],
    ),
    "premium": PlanLimits(
        name="premium",
        max_connections=999,
        max_accounts=999,
        max_transactions_month=999999,
        features=[
            "basic_dashboard",
            "reports",
            "export_csv",
            "recurrences",
            "ai_assistant",
            "patrimony",
            "projections",
            "pj_support",
        ],
    ),
}


def get_plan_limits(plan_name: str) -> PlanLimits:
    return PLANS.get(plan_name.lower(), PLANS["free"])
