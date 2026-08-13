"""
AI Job Hunter - Asset Service

Business logic for generating and managing career assets.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.agents.orchestrator import run_agent_pipeline
from backend.assets.models import ApplicationAsset
from backend.resume.service import ResumeService
from backend.utils.exceptions import NotFoundException
from backend.utils.helpers import generate_id
from backend.utils.logger import get_logger

logger = get_logger("assets.service")


class AssetService:
    """Service for career assets generation and persistence."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def generate_cover_letter(
        self,
        user_id: str,
        resume_id: str,
        job_description: str,
        job_title: str = "",
        company_name: str = "",
        hiring_manager_name: str = "",
    ) -> ApplicationAsset:
        # Fetch resume text
        resume_service = ResumeService(self.db)
        resume = await resume_service.get_resume(resume_id, user_id)

        result = await run_agent_pipeline(
            intent="generate_cover_letter",
            state_overrides={
                "user_id": user_id,
                "resume_id": resume_id,
                "resume_text": resume.raw_text,
                "job_description": job_description,
                "job_title": job_title or "Software Engineer",
                "job_company": company_name or "Target Company",
            },
        )

        cover_letter_text = result.get("cover_letter", "")

        asset = ApplicationAsset(
            id=generate_id(),
            user_id=user_id,
            resume_id=resume_id,
            asset_type="cover_letter",
            title=f"Cover Letter - {company_name or 'Company'} ({job_title or 'Role'})",
            content=cover_letter_text,
            meta_info={
                "job_title": job_title,
                "company_name": company_name,
                "hiring_manager_name": hiring_manager_name,
            },
        )

        self.db.add(asset)
        await self.db.commit()
        await self.db.refresh(asset)
        return asset

    async def generate_recruiter_message(
        self,
        user_id: str,
        resume_id: str,
        job_title: str,
        company_name: str,
        recruiter_name: str = "",
        platform: str = "LinkedIn",
    ) -> ApplicationAsset:
        resume_service = ResumeService(self.db)
        resume = await resume_service.get_resume(resume_id, user_id)

        result = await run_agent_pipeline(
            intent="generate_recruiter_message",
            state_overrides={
                "user_id": user_id,
                "resume_id": resume_id,
                "resume_text": resume.raw_text,
                "job_title": job_title,
                "job_company": company_name,
                "outreach_platform": platform,
            },
        )

        message_text = result.get("recruiter_message", "")

        asset = ApplicationAsset(
            id=generate_id(),
            user_id=user_id,
            resume_id=resume_id,
            asset_type="recruiter_message",
            title=f"Outreach Message - {company_name} ({platform})",
            content=message_text,
            meta_info={
                "job_title": job_title,
                "company_name": company_name,
                "platform": platform,
                "recruiter_name": recruiter_name,
            },
        )

        self.db.add(asset)
        await self.db.commit()
        await self.db.refresh(asset)
        return asset

    async def generate_interview_prep(
        self,
        user_id: str,
        resume_id: str,
        job_description: str,
        company_name: str,
        role_title: str = "",
    ) -> ApplicationAsset:
        resume_service = ResumeService(self.db)
        resume = await resume_service.get_resume(resume_id, user_id)

        result = await run_agent_pipeline(
            intent="prepare_interview",
            state_overrides={
                "user_id": user_id,
                "resume_id": resume_id,
                "resume_text": resume.raw_text,
                "job_description": job_description,
                "job_company": company_name,
                "job_title": role_title or "Software Engineer",
            },
        )

        prep_data = result.get("interview_prep", {})
        import json
        content_str = json.dumps(prep_data)

        asset = ApplicationAsset(
            id=generate_id(),
            user_id=user_id,
            resume_id=resume_id,
            asset_type="interview_prep",
            title=f"Interview Guide - {company_name} ({role_title or 'Role'})",
            content=content_str,
            meta_info={
                "role_title": role_title,
                "company_name": company_name,
            },
        )

        self.db.add(asset)
        await self.db.commit()
        await self.db.refresh(asset)
        return asset

    async def list_assets(self, user_id: str, asset_type: str = "") -> list[ApplicationAsset]:
        stmt = select(ApplicationAsset).where(ApplicationAsset.user_id == user_id)
        if asset_type:
            stmt = stmt.where(ApplicationAsset.asset_type == asset_type)
        stmt = stmt.order_by(ApplicationAsset.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_asset(self, asset_id: str, user_id: str) -> ApplicationAsset:
        stmt = select(ApplicationAsset).where(ApplicationAsset.id == asset_id, ApplicationAsset.user_id == user_id)
        res = await self.db.execute(stmt)
        asset = res.scalar_one_or_none()
        if not asset:
            raise NotFoundException(f"Asset '{asset_id}' not found")
        return asset

    async def delete_asset(self, asset_id: str, user_id: str) -> None:
        asset = await self.get_asset(asset_id, user_id)
        await self.db.delete(asset)
        await self.db.commit()
