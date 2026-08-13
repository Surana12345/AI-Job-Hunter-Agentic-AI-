"""
AI Job Hunter - Database Migrations

Handles automatic table creation on application startup.
For a production app, consider migrating to Alembic for versioned migrations.
"""

from __future__ import annotations

from backend.database.base import Base
from backend.database.engine import async_engine
from backend.utils.logger import get_logger

logger = get_logger("database.migrations")


async def create_all_tables() -> None:
    """Create all database tables defined by ORM models.

    This runs on application startup. Tables that already exist
    are left unchanged (create_all is idempotent).
    """
    # Import all models so they register with Base.metadata
    # These imports are intentionally inside the function to avoid circular imports
    import backend.auth.models  # noqa: F401
    import backend.resume.models  # noqa: F401
    import backend.jobs.models  # noqa: F401
    import backend.assets.models  # noqa: F401
    import backend.tracker.models  # noqa: F401

    logger.info("Creating database tables...")

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables created successfully")


async def drop_all_tables() -> None:
    """Drop all database tables. USE WITH CAUTION — destroys all data."""
    logger.warning("Dropping all database tables!")

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    logger.info("All database tables dropped")
