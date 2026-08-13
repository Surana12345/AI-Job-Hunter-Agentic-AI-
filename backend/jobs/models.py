"""
AI Job Hunter - Job ORM Model

Stores discovered job listings with metadata, descriptions,
and analysis results.
"""

from __future__ import annotations

from sqlalchemy import Boolean, Column, Float, ForeignKey, JSON, String, Text

from backend.database.base import Base


class Job(Base):
    """Job listing database model."""

    __tablename__ = "jobs"

    user_id = Column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=True)
    job_type = Column(String(50), nullable=True)  # full-time, part-time, contract, remote
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    currency = Column(String(10), nullable=True)
    description = Column(Text, nullable=False, default="")
    url = Column(String(1000), nullable=True)
    source = Column(String(50), nullable=False, default="manual")  # adzuna, remotive, manual
    source_id = Column(String(255), nullable=True)  # External API ID
    keywords = Column(JSON, nullable=True)
    ats_score = Column(Float, nullable=True)
    is_saved = Column(Boolean, default=False, nullable=False)
    is_applied = Column(Boolean, default=False, nullable=False)
    company_info = Column(JSON, nullable=True)  # Cached company research
