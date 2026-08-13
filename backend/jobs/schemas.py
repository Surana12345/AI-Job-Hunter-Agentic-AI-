"""
AI Job Hunter - Job Pydantic Schemas

Request/response schemas for job search, listing, and management.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class JobSearchRequest(BaseModel):
    """Request to search for jobs."""

    query: str = Field(..., min_length=2, description="Job search query (e.g. 'ML Engineer')")
    location: str = Field("", description="Location filter (e.g. 'Remote', 'New York')")
    job_type: str = Field("", description="Job type: full-time, part-time, contract, remote")
    max_results: int = Field(20, ge=1, le=50, description="Max results to return")


class JobResponse(BaseModel):
    """Full job listing response."""

    id: str
    user_id: str
    title: str
    company: str
    location: Optional[str] = None
    job_type: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: Optional[str] = None
    description: str
    url: Optional[str] = None
    source: str
    keywords: Optional[list[str]] = None
    ats_score: Optional[float] = None
    is_saved: bool
    is_applied: bool
    company_info: Optional[dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class JobListItem(BaseModel):
    """Lightweight job item for list views."""

    id: str
    title: str
    company: str
    location: Optional[str] = None
    job_type: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: Optional[str] = None
    url: Optional[str] = None
    source: str
    ats_score: Optional[float] = None
    is_saved: bool
    is_applied: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class JobSearchResult(BaseModel):
    """Result from an external job search."""

    title: str
    company: str
    location: str = ""
    job_type: str = ""
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: str = ""
    description: str = ""
    url: str = ""
    source: str = ""
    source_id: str = ""


class CompanyResearchRequest(BaseModel):
    """Request to research a company."""

    company_name: str = Field(..., min_length=1)
    job_title: str = Field("", description="Job title for context")


class CompanyResearchResponse(BaseModel):
    """Company research results."""

    name: str
    summary: str = ""
    website: str = ""
    tech_stack: list[str] = Field(default_factory=list)
    products: list[str] = Field(default_factory=list)
    values: list[str] = Field(default_factory=list)
    interview_style: str = ""
    recent_news: list[str] = Field(default_factory=list)
