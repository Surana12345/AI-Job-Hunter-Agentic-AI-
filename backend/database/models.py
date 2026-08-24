"""
CareerOps - SQLAlchemy Database Models

Complete ORM schema matching the CareerOps Product Blueprint:
users, profiles, resumes, skills, jobs, companies, applications,
application_events, generated_documents, emails, contacts, interviews,
offers, agent_runs, automation_settings.
"""

from __future__ import annotations

from typing import Any, Optional
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    automation_settings = relationship("AutomationSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"

    user_id: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    experience_level: Mapped[str] = mapped_column(String(50), default="Mid Level")
    education: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, default=dict)
    skills: Mapped[Optional[list[str]]] = mapped_column(JSON, default=list)
    projects: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(JSON, default=list)
    experience: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(JSON, default=list)
    certifications: Mapped[Optional[list[str]]] = mapped_column(JSON, default=list)
    preferred_roles: Mapped[Optional[list[str]]] = mapped_column(JSON, default=list)
    locations: Mapped[Optional[list[str]]] = mapped_column(JSON, default=list)
    salary_expectation: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, default=dict)
    raw_data: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, default=dict)

    user = relationship("User", back_populates="profile")


class Resume(Base):
    __tablename__ = "resumes"

    user_id: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), index=True, nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_skills: Mapped[Optional[list[str]]] = mapped_column(JSON, default=list)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="resumes")


class Job(Base):
    __tablename__ = "jobs"

    user_id: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), index=True, nullable=False)
    company: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255))
    job_type: Mapped[Optional[str]] = mapped_column(String(50))
    salary_min: Mapped[Optional[float]] = mapped_column(Float)
    salary_max: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[Optional[str]] = mapped_column(String(10), default="USD")
    description: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(1000))
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    source_id: Mapped[Optional[str]] = mapped_column(String(255))
    keywords: Mapped[Optional[list[str]]] = mapped_column(JSON, default=list)
    dedup_key: Mapped[Optional[str]] = mapped_column(String(255), index=True)

    user = relationship("User", back_populates="jobs")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")


class Company(Base):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    website: Mapped[Optional[str]] = mapped_column(String(255))
    tech_stack: Mapped[Optional[list[str]]] = mapped_column(JSON, default=list)
    culture_summary: Mapped[Optional[str]] = mapped_column(Text)
    interview_tips: Mapped[Optional[list[str]]] = mapped_column(JSON, default=list)


class Application(Base):
    __tablename__ = "applications"

    user_id: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), index=True, nullable=False)
    job_id: Mapped[str] = mapped_column(String(32), ForeignKey("jobs.id"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), index=True, default="DISCOVERED")
    match_score: Mapped[float] = mapped_column(Float, default=0.0)
    score_breakdown: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, default=dict)
    automation_level: Mapped[str] = mapped_column(String(20), default="ASSISTED")
    applied_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    events = relationship("ApplicationEvent", back_populates="application", cascade="all, delete-orphan")


class ApplicationEvent(Base):
    __tablename__ = "application_events"

    application_id: Mapped[str] = mapped_column(String(32), ForeignKey("applications.id"), index=True, nullable=False)
    from_status: Mapped[str] = mapped_column(String(50), nullable=False)
    to_status: Mapped[str] = mapped_column(String(50), nullable=False)
    event_details: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, default=dict)

    application = relationship("Application", back_populates="events")


class OutreachEmail(Base):
    __tablename__ = "emails"

    user_id: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), index=True, nullable=False)
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    recipient_name: Mapped[Optional[str]] = mapped_column(String(255))
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="DRAFT")


class AutomationSettings(Base):
    __tablename__ = "automation_settings"

    user_id: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), unique=True, index=True, nullable=False)
    auto_apply_threshold: Mapped[int] = mapped_column(Integer, default=90)
    assisted_threshold: Mapped[int] = mapped_column(Integer, default=80)
    review_threshold: Mapped[int] = mapped_column(Integer, default=70)
    max_daily_applications: Mapped[int] = mapped_column(Integer, default=25)
    require_human_review: Mapped[bool] = mapped_column(Boolean, default=True)

    user = relationship("User", back_populates="automation_settings")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    user_id: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), index=True, nullable=False)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    intent: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    trajectory: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, default=dict)


class ApplicationAsset(Base):
    __tablename__ = "application_assets"

    user_id: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), index=True, nullable=False)
    job_id: Mapped[Optional[str]] = mapped_column(String(32), ForeignKey("jobs.id"))
    resume_id: Mapped[Optional[str]] = mapped_column(String(32), ForeignKey("resumes.id"))
    asset_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    meta_info: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, default=dict)

