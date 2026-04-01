from __future__ import annotations

from uuid import UUID

from jose import JWTError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.security import decode_token
from app.core.tenant_context import set_current_tenant_id

# Routes that don't require tenant context
PUBLIC_PATHS = {
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
}

PUBLIC_PREFIXES = (
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/billing/webhook",
    "/api/v1/webhooks/pluggy",
)


class TenantContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Reset tenant context
        set_current_tenant_id(None)

        path = request.url.path

        # Skip public routes
        if path in PUBLIC_PATHS or path.startswith(PUBLIC_PREFIXES):
            return await call_next(request)

        # Extract tenant_id from JWT (header or cookie)
        token = None
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
        else:
            token = request.cookies.get("access_token")

        if token:
            try:
                payload = decode_token(token)
                tenant_id_str = payload.get("tenant_id")
                if tenant_id_str:
                    set_current_tenant_id(UUID(tenant_id_str))
            except (JWTError, ValueError):
                pass  # Auth endpoint will handle 401

        return await call_next(request)
