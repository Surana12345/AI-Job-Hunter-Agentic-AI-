"""
AI Job Hunter - SQLAlchemy Declarative Base

Provides the base class for all ORM models with common columns
(id, created_at, updated_at) that every table inherits.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from backend.utils.helpers import generate_id


class Base(DeclarativeBase):
    """Base class for all database models.

    Provides:
        - id: Primary key (UUID hex string)
        - created_at: Auto-set creation timestamp (UTC)
        - updated_at: Auto-updated modification timestamp (UTC)
    """

    id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True,
        default=generate_id,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id!r})>"
