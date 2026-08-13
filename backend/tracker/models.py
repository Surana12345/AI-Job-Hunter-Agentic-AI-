"""
AI Job Hunter - Application Tracker ORM Model

Tracks job applications, status transitions, notes, and dates.
"""

from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, Text

from backend.database.base import Base


class ApplicationTrack(Base):
    """Application tracking database model.

    Statuses: 'saved', 'applied', 'interview', 'offer', 'rejected'
    """

    __tablename__ = "application_tracks"

    user_id = Column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(String(32), ForeignKey("jobs.id"), nullable=True, index=True)
    job_title = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default="saved", index=True)
    applied_date = Column(DateTime, nullable=True)
    follow_up_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    contact_person = Column(String(255), nullable=True)
    salary_offered = Column(String(100), nullable=True)
