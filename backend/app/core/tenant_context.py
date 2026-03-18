"""Tenant context utilities for request-scoped tenant isolation.

Provides helpers to read the current tenant_id from the request state and
configure the database session with the PostgreSQL ``app.current_tenant_id``
setting so that Row-Level Security policies enforce tenant isolation at
the database layer.
"""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory


def get_current_tenant_id(request: Request) -> str:
    """Read the tenant_id that :class:`TenantMiddleware` placed on
    ``request.state``.

    Returns the tenant_id as a string (UUID in text form).
    Raises 401 if not present (should never happen for protected routes
    because the middleware already rejects those requests).
    """
    tenant_id: str | None = getattr(request.state, "tenant_id", None)
    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant context not available",
        )
    return tenant_id


async def get_db_with_tenant(
    tenant_id: str = Depends(get_current_tenant_id),
) -> AsyncGenerator[AsyncSession, None]:
    """Yield an async DB session with the PostgreSQL ``app.current_tenant_id``
    session variable set so that RLS policies can enforce tenant isolation.

    For SQLite (used in tests), the ``SET LOCAL`` is skipped because SQLite
    does not support ``current_setting``.
    """
    is_testing = os.getenv("TESTING") == "1"

    async with async_session_factory() as session:
        try:
            if not is_testing:
                # Set the tenant context for RLS on PostgreSQL
                await session.execute(
                    text("SET LOCAL app.current_tenant_id = :tid"),
                    {"tid": tenant_id},
                )
            yield session
        finally:
            await session.close()
