from __future__ import annotations

import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


def _get_database_url() -> str:
    if os.environ.get("TESTING") == "1":
        return "sqlite+aiosqlite:///./test.db"
    return settings.DATABASE_URL


def _get_engine_kwargs() -> dict:
    url = _get_database_url()
    kwargs: dict = {"echo": settings.DEBUG}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    else:
        kwargs["pool_size"] = 20
        kwargs["max_overflow"] = 10
    return kwargs


engine = create_async_engine(_get_database_url(), **_get_engine_kwargs())

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
