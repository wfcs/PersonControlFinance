"""Re-export every model so Alembic's ``target_metadata`` picks them all up."""

from app.models.base import Base  # noqa: F401
from app.models.tenant import Tenant  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.account import Account  # noqa: F401
from app.models.category import Category  # noqa: F401
from app.models.transaction import Transaction  # noqa: F401
from app.models.goal import Goal  # noqa: F401
from app.models.recurrence import Recurrence  # noqa: F401
from app.models.webhook_log import WebhookLog  # noqa: F401
