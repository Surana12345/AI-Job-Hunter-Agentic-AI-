"""
AI Job Hunter - Resume Service

Business logic for resume upload, parsing, ATS analysis, and tailoring.
Orchestrates file storage, text extraction, LLM analysis, and vector storage.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.agents.orchestrator import run_agent_pipeline
from backend.agents.tools.vector_tools import store_resume_embedding
from backend.config import get_settings
from backend.resume.models import Resume
from backend.resume.parser import extract_text, validate_file_type
from backend.utils.exceptions import NotFoundException, BadRequestException
from backend.utils.helpers import generate_id, sanitize_filename
from backend.utils.logger import get_logger

logger = get_logger("resume.service")


class ResumeService:
    """Service layer for resume operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.settings = get_settings()

    async def upload_resume(
        self,
        user_id: str,
        file: UploadFile,
        is_primary: bool = False,
    ) -> Resume:
        """Upload, save, extract text, and store a resume.

        Args:
            user_id: The owning user's ID.
            file: The uploaded file.
            is_primary: Whether to set as primary resume.

        Returns:
            The created Resume record.
        """
        # Validate file type
        content_type = validate_file_type(
            file.content_type or "", file.filename or "unknown"
        )

        # Generate unique ID and safe filename
        resume_id = generate_id()
        safe_name = sanitize_filename(file.filename or "resume")
        file_path = Path(self.settings.upload_dir) / user_id / f"{resume_id}_{safe_name}"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Save file to disk
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        logger.info("Resume file saved", resume_id=resume_id, path=str(file_path))

        # Extract text
        try:
            raw_text = extract_text(str(file_path), content_type)
        except Exception as e:
            # Clean up file on extraction failure
            file_path.unlink(missing_ok=True)
            raise BadRequestException(f"Failed to extract text from file: {e}")

        if not raw_text.strip():
            file_path.unlink(missing_ok=True)
            raise BadRequestException("Could not extract any text from the uploaded file")

        # If setting as primary, unset any existing primary
        if is_primary:
            await self._unset_primary(user_id)

        # Create database record
        resume = Resume(
            id=resume_id,
            user_id=user_id,
            filename=file.filename or "resume",
            file_path=str(file_path),
            file_type=content_type,
            raw_text=raw_text,
            is_primary=is_primary,
        )

        self.db.add(resume)
        await self.db.commit()
        await self.db.refresh(resume)

        logger.info(
            "Resume uploaded successfully",
            resume_id=resume_id,
            user_id=user_id,
            chars=len(raw_text),
        )

        return resume

    async def parse_resume(self, resume_id: str, user_id: str) -> Resume:
        """Parse a resume using the LLM agent to extract structured data.

        Args:
            resume_id: The resume ID.
            user_id: The owning user's ID.

        Returns:
            Updated Resume with parsed_data and skills.
        """
        resume = await self.get_resume(resume_id, user_id)

        if not resume.raw_text:
            raise BadRequestException("Resume has no text content to parse")

        # Run the resume parser agent
        result = await run_agent_pipeline(
            intent="parse_resume",
            state_overrides={
                "user_id": user_id,
                "resume_id": resume_id,
                "resume_text": resume.raw_text,
            },
        )

        if result.get("error"):
            raise BadRequestException(f"Resume parsing failed: {result['error']}")

        # Update the resume record
        resume.parsed_data = result.get("resume_data", {})
        resume.skills = result.get("resume_skills", [])

        await self.db.commit()
        await self.db.refresh(resume)

        # Store embedding in vector DB
        try:
            await store_resume_embedding(
                resume_id=resume_id,
                resume_text=resume.raw_text,
                metadata={
                    "user_id": user_id,
                    "filename": resume.filename,
                    "skills": ",".join(resume.skills or []),
                },
            )
        except Exception as e:
            logger.warning("Failed to store resume embedding", error=str(e))

        logger.info(
            "Resume parsed",
            resume_id=resume_id,
            skills_count=len(resume.skills or []),
        )

        return resume

    async def analyze_ats(
        self,
        resume_id: str,
        user_id: str,
        job_description: str,
        job_title: str = "",
        job_company: str = "",
    ) -> dict[str, Any]:
        """Run ATS compatibility analysis between a resume and job description.

        Args:
            resume_id: The resume ID.
            user_id: The owning user's ID.
            job_description: The full job description text.
            job_title: Optional job title.
            job_company: Optional company name.

        Returns:
            ATS analysis results dict.
        """
        resume = await self.get_resume(resume_id, user_id)

        if not resume.raw_text:
            raise BadRequestException("Resume has no text content for ATS analysis")

        result = await run_agent_pipeline(
            intent="analyze_ats",
            state_overrides={
                "user_id": user_id,
                "resume_id": resume_id,
                "resume_text": resume.raw_text,
                "job_description": job_description,
                "job_title": job_title,
                "job_company": job_company,
            },
        )

        if result.get("error"):
            raise BadRequestException(f"ATS analysis failed: {result['error']}")

        ats_result = result.get("ats_result", {})
        ats_result["resume_id"] = resume_id

        logger.info(
            "ATS analysis complete",
            resume_id=resume_id,
            score=ats_result.get("overall_score"),
        )

        return ats_result

    async def get_resume(self, resume_id: str, user_id: str) -> Resume:
        """Get a specific resume belonging to a user.

        Args:
            resume_id: The resume ID.
            user_id: The owning user's ID.

        Returns:
            The Resume record.

        Raises:
            NotFoundException: If resume not found or doesn't belong to user.
        """
        stmt = select(Resume).where(
            Resume.id == resume_id,
            Resume.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        resume = result.scalar_one_or_none()

        if not resume:
            raise NotFoundException(f"Resume '{resume_id}' not found")

        return resume

    async def list_resumes(self, user_id: str) -> list[Resume]:
        """List all resumes for a user.

        Args:
            user_id: The user's ID.

        Returns:
            List of Resume records.
        """
        stmt = (
            select(Resume)
            .where(Resume.user_id == user_id)
            .order_by(Resume.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete_resume(self, resume_id: str, user_id: str) -> None:
        """Delete a resume and its file.

        Args:
            resume_id: The resume ID.
            user_id: The owning user's ID.
        """
        resume = await self.get_resume(resume_id, user_id)

        # Delete file from disk
        file_path = Path(resume.file_path)
        if file_path.exists():
            file_path.unlink()

        await self.db.delete(resume)
        await self.db.commit()

        logger.info("Resume deleted", resume_id=resume_id)

    async def set_primary(self, resume_id: str, user_id: str) -> Resume:
        """Set a resume as the primary/active resume.

        Args:
            resume_id: The resume ID.
            user_id: The owning user's ID.

        Returns:
            Updated Resume record.
        """
        await self._unset_primary(user_id)

        resume = await self.get_resume(resume_id, user_id)
        resume.is_primary = True
        await self.db.commit()
        await self.db.refresh(resume)

        logger.info("Primary resume set", resume_id=resume_id)
        return resume

    async def _unset_primary(self, user_id: str) -> None:
        """Unset any existing primary resume for a user."""
        stmt = select(Resume).where(
            Resume.user_id == user_id,
            Resume.is_primary == True,
        )
        result = await self.db.execute(stmt)
        for resume in result.scalars().all():
            resume.is_primary = False
        await self.db.flush()
