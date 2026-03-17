"""Decorator para validar isolamento multi-tenant em endpoints."""

from functools import wraps
from typing import Callable, Any
from uuid import UUID

from fastapi import HTTPException, status

from app.core.deps import CurrentUser
from app.core.tenant_context import get_current_tenant_id


def validate_tenant_access(
    param_name: str = "tenant_id",
) -> Callable:
    """
    Decorator que valida se o tenant_id do parâmetro corresponde ao do usuário autenticado.
    
    Uso:
        @validate_tenant_access("tenant_id")
        async def my_endpoint(tenant_id: UUID, current_user: AuthUser):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # extrair tenant_id do contexto
            current_tenant = get_current_tenant_id()

            if not current_tenant:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Tenant context não foi carregado",
                )

            # Se o endpoint tem um parâmetro de tenant_id, validar
            if param_name in kwargs:
                requested_tenant = kwargs[param_name]
                if isinstance(requested_tenant, str):
                    requested_tenant = UUID(requested_tenant)

                if requested_tenant != current_tenant:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Você não tem acesso a este recurso",
                    )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_tenant_context(func: Callable) -> Callable:
    """
    Decorator simples que verifica se tenant_id está no contexto.
    Útil para endpoints que não têm tenant_id como parâmetro mas precisam dele.
    """

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not get_current_tenant_id():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant context não foi carregado",
            )
        return await func(*args, **kwargs)

    return wrapper
