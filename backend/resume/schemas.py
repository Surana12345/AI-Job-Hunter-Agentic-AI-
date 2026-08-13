"""
AI Job Hunter - Resume Pydantic Schemas

Request/response schemas for resume upload, parsing, and retrieval.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ResumeUploadResponse(BaseModel):
    """Response after uploading a resume."""

    id: str
    filename: str
    file_type: str
    is_primary: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ResumeResponse(BaseModel):
    """Full resume response with parsed data."""

    id: str
    user_id: str
    filename: str
    file_type: str
    raw_text: str
    parsed_data: Optional[dict[str, Any]] = None
    skills: Optional[list[str]] = None
    is_primary: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ResumeListItem(BaseModel):
    """Lightweight resume item for list views."""

    id: str
    filename: str
    file_type: str
    is_primary: bool
    skills_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class ResumeParsedData(BaseModel):
    """Structured resume data returned after LLM parsing."""

    full_name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    summary: str = ""
    skills: list[str] = Field(default_factory=list)
    experience: list[dict[str, Any]] = Field(default_factory=list)
    education: list[dict[str, Any]] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    projects: list[dict[str, Any]] = Field(default_factory=list)


class ATSAnalysisRequest(BaseModel):
    """Request to run ATS analysis on a resume against a job description."""

    resume_id: str
    job_description: str
    job_title: Optional[str] = ""
    job_company: Optional[str] = ""


class ATSAnalysisResponse(BaseModel):
    """ATS analysis result."""

    resume_id: str
    overall_score: float
    keyword_match_score: float
    skills_match_score: float
    experience_match_score: float
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    detailed_feedback: str = ""


class ResumeTailorRequest(BaseModel):
    """Request to tailor a resume for a specific job."""

    resume_id: str
    job_description: str
    job_title: Optional[str] = ""


class ResumeTailorResponse(BaseModel):
    """Response with tailored resume content."""

    resume_id: str
    original_skills: list[str] = Field(default_factory=list)
    tailored_resume: str
    changes_made: list[str] = Field(default_factory=list)
