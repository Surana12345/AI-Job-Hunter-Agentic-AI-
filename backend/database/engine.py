"""
AI Job Hunter - SQLAlchemy Async Engine & Session Factory

Provides the async database engine and session factory for all
database operations across the application.
"""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.config import get_settings

settings = get_settings()

# Create async engine with SQLite-specific optimizations
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    # SQLite doesn't support pool_size, but we set connect_args
    connect_args={"check_same_thread": False},
)

# Session factory
async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session.

    Usage in route handlers:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_async_session)):
            ...

    Yields:
        An AsyncSession that is automatically closed after use.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
