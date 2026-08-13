"""
AI Job Hunter - Application Tracker Schemas

Pydantic schemas for tracking job applications and computing analytics.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ApplicationTrackCreate(BaseModel):
    """Schema to log/create a tracked application."""

    job_id: Optional[str] = None
    job_title: str = Field(..., min_length=1)
    company_name: str = Field(..., min_length=1)
    location: Optional[str] = ""
    status: str = Field("saved", description="Status: saved, applied, interview, offer, rejected")
    notes: Optional[str] = ""
    contact_person: Optional[str] = ""


class ApplicationTrackUpdate(BaseModel):
    """Schema to update an existing tracked application."""

    status: Optional[str] = None
    notes: Optional[str] = None
    applied_date: Optional[datetime] = None
    follow_up_date: Optional[datetime] = None
    contact_person: Optional[str] = None
    salary_offered: Optional[str] = None


class ApplicationTrackResponse(BaseModel):
    """Tracked application response."""

    id: str
    user_id: str
    job_id: Optional[str] = None
    job_title: str
    company_name: str
    location: Optional[str] = None
    status: str
    applied_date: Optional[datetime] = None
    follow_up_date: Optional[datetime] = None
    notes: Optional[str] = None
    contact_person: Optional[str] = None
    salary_offered: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AnalyticsSummary(BaseModel):
    """Application stats and conversion metric summary."""

    total_tracked: int = 0
    saved_count: int = 0
    applied_count: int = 0
    interview_count: int = 0
    offer_count: int = 0
    rejected_count: int = 0
    interview_rate: float = 0.0  # (interview + offer) / max(applied, 1) * 100
    offer_rate: float = 0.0      # offer / max(applied, 1) * 100
