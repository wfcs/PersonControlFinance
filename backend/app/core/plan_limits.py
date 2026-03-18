"""Plan definitions and resource limits for multi-tenant SaaS tiers."""

from enum import Enum


class Plan(str, Enum):
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"


PLAN_LIMITS: dict[Plan, dict] = {
    Plan.FREE: {
        "max_accounts": 2,
        "max_categories": 10,
        "max_goals": 3,
        "open_finance": False,
        "ai_assistant": False,
        "export_csv": False,
    },
    Plan.PRO: {
        "max_accounts": 10,
        "max_categories": 50,
        "max_goals": 20,
        "open_finance": True,
        "ai_assistant": False,
        "export_csv": True,
    },
    Plan.PREMIUM: {
        "max_accounts": -1,  # unlimited
        "max_categories": -1,
        "max_goals": -1,
        "open_finance": True,
        "ai_assistant": True,
        "export_csv": True,
    },
}


# Mapping from resource name to the limit key in PLAN_LIMITS
RESOURCE_LIMIT_KEYS: dict[str, str] = {
    "accounts": "max_accounts",
    "categories": "max_categories",
    "goals": "max_goals",
}
