"""Multi-tenant context manager e helpers para isolamento automático de dados."""

from contextvars import ContextVar
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

# Context variables para armazenar tenant_id e user_id por request
_tenant_id_ctx: ContextVar[Optional[UUID]] = ContextVar("tenant_id", default=None)
_user_id_ctx: ContextVar[Optional[UUID]] = ContextVar("user_id", default=None)


def set_current_tenant_id(tenant_id: UUID) -> None:
    """Define tenant_id para o request atual."""
    _tenant_id_ctx.set(tenant_id)


def get_current_tenant_id() -> Optional[UUID]:
    """Retorna tenant_id do request atual."""
    return _tenant_id_ctx.get()


def set_current_user_id(user_id: UUID) -> None:
    """Define user_id para o request atual."""
    _user_id_ctx.set(user_id)


def get_current_user_id() -> Optional[UUID]:
    """Retorna user_id do request atual."""
    return _user_id_ctx.get()


async def apply_tenant_context(session: AsyncSession, tenant_id: UUID, user_id: UUID) -> None:
    """
    Aplica context de tenant_id e user_id:
    1. Define context variables (para acesso local)
    2. Define session variables (para RLS policies no PostgreSQL)
    """
    # Definir context variables
    set_current_tenant_id(tenant_id)
    set_current_user_id(user_id)

    # Definir session variables no PostgreSQL para RLS
    await session.execute(
        f"SET app.current_tenant_id = '{tenant_id}';"
    )
    await session.execute(
        f"SET app.current_user_id = '{user_id}';"
    )


async def clear_tenant_context(session: AsyncSession) -> None:
    """Limpa context e session variables após request."""
    _tenant_id_ctx.set(None)
    _user_id_ctx.set(None)

    # Limpar session variables
    try:
        await session.execute("RESET app.current_tenant_id;")
        await session.execute("RESET app.current_user_id;")
    except Exception:
        # Session pode ter sido encerrada
        pass
