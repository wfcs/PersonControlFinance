"""Async SQLAlchemy engine and session factory."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


def _build_engine():
    """Build the async engine with driver-appropriate pool settings."""
    kwargs: dict = {
        "echo": settings.DEBUG,
    }
    # SQLite (used in tests) does not support pool_size / max_overflow
    if not settings.DATABASE_URL.startswith("sqlite"):
        kwargs["pool_pre_ping"] = True
        kwargs["pool_size"] = 10
        kwargs["max_overflow"] = 20
    return create_async_engine(settings.DATABASE_URL, **kwargs)


engine = _build_engine()

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
