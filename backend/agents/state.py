"""
AI Job Hunter - Shared Agent State

Defines the TypedDict state contract that flows through the LangGraph
orchestrator. Every agent reads from and writes to this shared state.
"""

from __future__ import annotations

from typing import Any, TypedDict


class ResumeData(TypedDict, total=False):
    """Structured resume data extracted by the resume parser agent."""

    raw_text: str
    full_name: str
    email: str
    phone: str
    linkedin: str
    summary: str
    skills: list[str]
    experience: list[dict[str, Any]]
    education: list[dict[str, Any]]
    certifications: list[str]
    projects: list[dict[str, Any]]


class ATSResult(TypedDict, total=False):
    """ATS analysis result produced by the ATS scorer agent."""

    overall_score: float
    keyword_match_score: float
    skills_match_score: float
    experience_match_score: float
    matched_keywords: list[str]
    missing_keywords: list[str]
    matched_skills: list[str]
    missing_skills: list[str]
    suggestions: list[str]
    detailed_feedback: str


class CompanyInfo(TypedDict, total=False):
    """Company research data gathered by the company research agent."""

    name: str
    website: str
    tech_stack: list[str]
    products: list[str]
    interview_style: str
    values: list[str]
    recent_news: list[str]
    glassdoor_rating: float
    summary: str


class AgentState(TypedDict, total=False):
    """Shared state that flows through the LangGraph orchestrator.

    Every agent node reads from and writes to this state. Fields are
    optional (total=False) so agents can incrementally build up the state.

    Sections:
        - User context: user_id, resume
        - Job context: job description, company
        - Agent outputs: ATS result, tailored resume, cover letter, etc.
        - Control flow: current_agent, next_agent, error, messages
    """

    # --- User Context ---
    user_id: str
    resume_id: str
    resume_text: str
    resume_data: ResumeData
    resume_skills: list[str]

    # --- Job Context ---
    job_id: str
    job_title: str
    job_company: str
    job_description: str
    job_keywords: list[str]
    job_location: str

    # --- Agent Outputs ---
    ats_result: ATSResult
    tailored_resume: str
    tailored_role: str
    cover_letter: str
    recruiter_message: str
    interview_questions: list[dict[str, str]]
    interview_talking_points: list[str]
    interview_question: str
    candidate_answer: str
    interview_evaluation: dict[str, Any]
    company_info: CompanyInfo

    # --- Control Flow ---
    current_agent: str
    next_agent: str
    intent: str
    error: str | None

    # --- Message History ---
    messages: list[dict[str, str]]
