"""Middleware FastAPI para aplicar tenant context em toda request."""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tenant_context import apply_tenant_context, clear_tenant_context
from app.db.session import get_session


class TenantContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware que:
    1. Extrai tenant_id do JWT token
    2. Aplica context variables e session variables para RLS
    3. Limpa context após request
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Endpoints que não precisam de autenticação (login, register, etc)
        public_endpoints = [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/docs",
            "/openapi.json",
            "/health",
        ]

        path = request.url.path
        if any(path.startswith(ep) for ep in public_endpoints):
            return await call_next(request)

        # Para endpoints protegidos, extrair tenant_id do token
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                from app.core.security import decode_token
                from uuid import UUID

                token = auth_header.replace("Bearer ", "")
                payload = decode_token(token)

                tenant_id = payload.get("tenant_id")
                user_id = payload.get("sub")

                if tenant_id and user_id:
                    # Criar nova session para este request
                    async_gen = get_session()
                    session: AsyncSession = await async_gen.__anext__()

                    try:
                        # Aplicar context para toda request
                        await apply_tenant_context(session, UUID(tenant_id), UUID(user_id))
                        response = await call_next(request)
                    finally:
                        # Limpar context e fechar session
                        await clear_tenant_context(session)
                        try:
                            await async_gen.__anext__()
                        except StopAsyncIteration:
                            pass
                        await session.close()

                    return response
            except Exception:
                # Se falhar na extração do token, deixar seguir
                # get_current_user vai validar e retornar erro
                pass

        return await call_next(request)
