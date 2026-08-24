"""
CareerOps - Profile API Router

Endpoints for retrieving, editing, and extracting canonical candidate profiles.
"""

from __future__ import annotations

from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import Profile
from backend.dependencies import get_current_user, get_db

router = APIRouter(prefix="/profile", tags=["Candidate Profile"])


class ProfileUpdateRequest(BaseModel):
    name: str = Field(..., description="Candidate Full Name")
    experience_level: str = Field("Senior Level")
    education: Optional[dict[str, Any]] = Field(default_factory=dict)
    skills: Optional[list[str]] = Field(default_factory=list)
    projects: Optional[list[dict[str, Any]]] = Field(default_factory=list)
    experience: Optional[list[dict[str, Any]]] = Field(default_factory=list)
    certifications: Optional[list[str]] = Field(default_factory=list)
    preferred_roles: Optional[list[str]] = Field(default_factory=list)
    locations: Optional[list[str]] = Field(default_factory=list)
    salary_expectation: Optional[dict[str, Any]] = Field(default_factory=dict)


@router.get("", summary="Get Canonical Candidate Profile")
async def get_profile(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user_id = current_user["sub"]
    stmt = select(Profile).where(Profile.user_id == user_id)
    res = await db.execute(stmt)
    prof = res.scalar_one_or_none()

    if not prof:
        return {
            "name": current_user.get("full_name", "Candidate"),
            "experience_level": "Senior Level",
            "education": {"degree": "B.S. Computer Science", "institution": "University"},
            "skills": ["Python", "FastAPI", "LangGraph", "Docker", "PostgreSQL"],
            "projects": [],
            "experience": [],
            "certifications": [],
            "preferred_roles": ["Senior Software Engineer", "AI Engineer"],
            "locations": ["Remote"],
            "salary_expectation": {"currency": "USD", "min_base": 130000, "target_base": 150000}
        }

    return {
        "id": prof.id,
        "name": prof.name,
        "experience_level": prof.experience_level,
        "education": prof.education,
        "skills": prof.skills,
        "projects": prof.projects,
        "experience": prof.experience,
        "certifications": prof.certifications,
        "preferred_roles": prof.preferred_roles,
        "locations": prof.locations,
        "salary_expectation": prof.salary_expectation,
    }


@router.post("", summary="Create or Update Profile")
async def save_profile(
    request: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user_id = current_user["sub"]
    stmt = select(Profile).where(Profile.user_id == user_id)
    res = await db.execute(stmt)
    prof = res.scalar_one_or_none()

    if not prof:
        prof = Profile(
            user_id=user_id,
            name=request.name,
            experience_level=request.experience_level,
            education=request.education,
            skills=request.skills,
            projects=request.projects,
            experience=request.experience,
            certifications=request.certifications,
            preferred_roles=request.preferred_roles,
            locations=request.locations,
            salary_expectation=request.salary_expectation,
        )
        db.add(prof)
    else:
        prof.name = request.name
        prof.experience_level = request.experience_level
        prof.education = request.education
        prof.skills = request.skills
        prof.projects = request.projects
        prof.experience = request.experience
        prof.certifications = request.certifications
        prof.preferred_roles = request.preferred_roles
        prof.locations = request.locations
        prof.salary_expectation = request.salary_expectation

    await db.commit()
    await db.refresh(prof)

    return {"message": "Profile updated successfully", "id": prof.id}
