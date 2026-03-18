"""Middleware that extracts tenant_id from the JWT in the Authorization header
and stores it in ``request.state`` for downstream dependencies."""

import logging

from jose import JWTError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.security import decode_token

logger = logging.getLogger(__name__)


class TenantMiddleware(BaseHTTPMiddleware):
    """Extract tenant_id from JWT and store in request state.

    Requests to paths in ``EXCLUDED_PATHS`` (login, register, docs, etc.)
    are forwarded without tenant extraction.
    """

    EXCLUDED_PATHS: set[str] = {
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/refresh",
        "/api/v1/auth/logout",
        "/api/v1/webhooks/pluggy",
    }

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        path = request.url.path

        # Skip excluded paths
        if path in self.EXCLUDED_PATHS:
            return await call_next(request)

        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid Authorization header"},
            )

        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_token(token)
        except JWTError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token"},
            )

        tenant_id = payload.get("tenant_id")
        if not tenant_id:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token missing tenant_id claim"},
            )

        # Store tenant_id in request state for downstream use
        request.state.tenant_id = tenant_id
        request.state.user_id = payload.get("sub")

        response = await call_next(request)
        return response
