"""
AI Job Hunter - Asset ORM Model

Stores generated application materials (cover letters, recruiter messages, interview guides).
"""

from __future__ import annotations

from sqlalchemy import Column, ForeignKey, JSON, String, Text

from backend.database.base import Base


class ApplicationAsset(Base):
    """Generated application asset database model.

    Attributes:
        user_id: Foreign key to owning user.
        job_id: Foreign key to target job (optional).
        resume_id: Foreign key to source resume (optional).
        asset_type: Type of asset ('cover_letter', 'recruiter_message', 'interview_prep').
        title: Descriptive title for asset.
        content: Main text content or JSON representation.
        meta_info: JSON metadata (e.g., recipient name, tone, key highlights).
    """

    __tablename__ = "application_assets"

    user_id = Column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(String(32), ForeignKey("jobs.id"), nullable=True, index=True)
    resume_id = Column(String(32), ForeignKey("resumes.id"), nullable=True)
    asset_type = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    meta_info = Column(JSON, nullable=True)
