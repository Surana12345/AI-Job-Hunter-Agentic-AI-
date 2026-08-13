"""
AI Job Hunter - Resume ORM Model

Stores resume metadata and parsed content. The actual file is saved
to disk; the database holds the structured extraction and analysis results.
"""

from __future__ import annotations

from sqlalchemy import Boolean, Column, ForeignKey, JSON, String, Text

from backend.database.base import Base


class Resume(Base):
    """Resume database model."""

    __tablename__ = "resumes"

    user_id = Column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(100), nullable=False)
    raw_text = Column(Text, nullable=False, default="")
    parsed_data = Column(JSON, nullable=True)
    skills = Column(JSON, nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)
