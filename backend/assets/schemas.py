"""
AI Job Hunter - Asset Pydantic Schemas

Request/response schemas for career asset generation and retrieval.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class CoverLetterRequest(BaseModel):
    """Request to generate a cover letter."""

    resume_id: str = Field(..., description="ID of candidate resume")
    job_description: str = Field(..., min_length=20, description="Job description text")
    job_title: str = Field("", description="Job title")
    company_name: str = Field("", description="Company name")
    hiring_manager_name: str = Field("", description="Hiring manager name if known")


class CoverLetterResponse(BaseModel):
    """Generated cover letter response."""

    id: str
    job_title: str
    company_name: str
    cover_letter: str
    created_at: datetime


class RecruiterMessageRequest(BaseModel):
    """Request to generate a recruiter outreach message."""

    resume_id: str = Field(..., description="ID of candidate resume")
    job_title: str = Field(..., description="Target job title")
    company_name: str = Field(..., description="Company name")
    recruiter_name: str = Field("", description="Recruiter/Hiring Manager name")
    platform: str = Field("LinkedIn", description="Platform: LinkedIn, Email, Twitter")


class RecruiterMessageResponse(BaseModel):
    """Generated recruiter message response."""

    id: str
    platform: str
    subject: str = ""
    message: str
    created_at: datetime


class InterviewPrepRequest(BaseModel):
    """Request to generate an interview preparation guide."""

    resume_id: str = Field(..., description="ID of candidate resume")
    job_description: str = Field(..., description="Target job description")
    company_name: str = Field(..., description="Company name")
    role_title: str = Field("", description="Role title")


class InterviewPrepResponse(BaseModel):
    """Generated interview preparation guide response."""

    id: str
    company_name: str
    role_title: str
    technical_questions: list[dict[str, Any]] = Field(default_factory=list)
    behavioral_questions: list[dict[str, Any]] = Field(default_factory=list)
    questions_to_ask_interviewer: list[str] = Field(default_factory=list)
    key_selling_points: list[str] = Field(default_factory=list)
    created_at: datetime


class AssetListItem(BaseModel):
    """Lightweight asset list item."""

    id: str
    asset_type: str
    title: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PDFExportRequest(BaseModel):
    """Request to export a compiled PDF application dossier."""

    job_title: str = Field("Software Engineer")
    company_name: str = Field("Target Company")
    cover_letter: Optional[str] = ""
    tailored_resume: Optional[str] = ""
    recruiter_message: Optional[str] = ""
    interview_prep: Optional[dict[str, Any]] = None


class MockInterviewRequest(BaseModel):
    """Request to evaluate a candidate's answer in a mock interview."""

    job_title: str = Field("Software Engineer")
    company_name: str = Field("Target Company")
    question: str = Field(..., description="The interview question asked")
    candidate_answer: str = Field(..., description="Candidate's response to evaluate")


class MockInterviewResponse(BaseModel):
    """Mock interview evaluation response."""

    score: int
    feedback: str
    improved_answer: str
    next_question: str


class SalaryNegotiationRequest(BaseModel):
    """Request to evaluate a job offer and draft counter-offer strategy."""

    job_title: str = Field(..., description="Target job title")
    company_name: str = Field(..., description="Company name")
    offered_base: int = Field(..., ge=1, description="Offered base salary in USD")
    offered_bonus: int = Field(0, description="Offered annual bonus in USD")
    offered_equity: int = Field(0, description="Offered equity/RSU value in USD")
    location: str = Field("Remote", description="Job location")
    target_counter: Optional[int] = Field(None, description="Optional counter goal")
    notes: Optional[str] = Field("", description="Additional candidate notes/priorities")


class SalaryNegotiationResponse(BaseModel):
    """Salary negotiation evaluation response."""

    market_range: dict[str, int]
    offer_assessment: str
    recommended_counter: int
    counter_offer_script: str
    key_levers: list[str]



