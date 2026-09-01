"""
AI Job Hunter - Job Service

Business logic for job search, storage, and management.
Aggregates results from multiple job source adapters.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.agents.tools.vector_tools import store_job_embedding
from backend.config import get_settings
from backend.jobs.models import Job
from backend.jobs.schemas import JobSearchResult
from backend.jobs.sources.adzuna import search_adzuna
from backend.jobs.sources.remotive import search_remotive
from backend.jobs.sources.jsearch import search_jsearch
from backend.jobs.sources.ats_scrapers import scrape_direct_ats_boards
from backend.utils.exceptions import NotFoundException
from backend.utils.helpers import generate_id
from backend.utils.logger import get_logger

logger = get_logger("jobs.service")


class JobService:
    """Service layer for job operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def search_jobs(
        self,
        user_id: str,
        query: str,
        location: str = "",
        job_type: str = "",
        max_results: int = 20,
    ) -> list[Job]:
        """Search for jobs across all configured sources and save results.

        Args:
            user_id: The searching user's ID.
            query: Job search query.
            location: Location filter.
            job_type: Job type filter.
            max_results: Max results per source.

        Returns:
            List of saved Job records.
        """
        logger.info("Searching jobs across omni-channel feeds", query=query, location=location)

        # Aggregate results from all sources
        all_results: list[JobSearchResult] = []

        # 1. Remotive (Remote developer feeds)
        try:
            remotive_results = await search_remotive(query=query, max_results=max_results)
            all_results.extend(remotive_results)
        except Exception as e:
            logger.warning("Remotive search failed", error=str(e))

        # 2. JSearch Multi-Aggregator (LinkedIn, Indeed, Glassdoor, ZipRecruiter)
        try:
            jsearch_results = await search_jsearch(query=query, location=location, job_type=job_type, max_results=max_results)
            all_results.extend(jsearch_results)
        except Exception as e:
            logger.warning("JSearch search failed", error=str(e))

        # 3. Direct ATS Board Crawlers (Greenhouse, Lever, Ashby)
        try:
            ats_results = await scrape_direct_ats_boards(query=query, max_results=10)
            all_results.extend(ats_results)
        except Exception as e:
            logger.warning("Direct ATS board search failed", error=str(e))

        # 4. Adzuna (if configured)
        settings = get_settings()
        if settings.adzuna_app_id and settings.adzuna_api_key:
            try:
                adzuna_results = await search_adzuna(
                    query=query, location=location, max_results=max_results
                )
                all_results.extend(adzuna_results)
            except Exception as e:
                logger.warning("Adzuna search failed", error=str(e))

        # Deduplicate by source_id or title+company
        seen = set()
        unique_results = []
        for r in all_results:
            key = f"{r.source}:{r.source_id}" if r.source_id else f"{r.title.lower().strip()}:{r.company.lower().strip()}"
            if key not in seen:
                seen.add(key)
                unique_results.append(r)

        # Save to database
        saved_jobs = []
        for result in unique_results:
            job = Job(
                id=generate_id(),
                user_id=user_id,
                title=result.title,
                company=result.company,
                location=result.location,
                job_type=result.job_type,
                salary_min=result.salary_min,
                salary_max=result.salary_max,
                currency=result.currency,
                description=result.description,
                url=result.url,
                source=result.source,
                source_id=result.source_id,
            )
            self.db.add(job)
            saved_jobs.append(job)

            # Store embedding for semantic search
            try:
                await store_job_embedding(
                    job_id=job.id,
                    job_text=f"{job.title} at {job.company}. {job.description[:500]}",
                    metadata={"title": job.title, "company": job.company, "source": job.source},
                )
            except Exception as e:
                logger.warning("Failed to store job embedding", error=str(e))

        await self.db.commit()

        logger.info("Jobs saved", count=len(saved_jobs))
        return saved_jobs

    async def list_jobs(
        self,
        user_id: str,
        saved_only: bool = False,
        limit: int = 50,
    ) -> list[Job]:
        """List jobs for a user.

        Args:
            user_id: The user's ID.
            saved_only: If True, only return saved/bookmarked jobs.
            limit: Max results.

        Returns:
            List of Job records.
        """
        stmt = select(Job).where(Job.user_id == user_id)
        if saved_only:
            stmt = stmt.where(Job.is_saved == True)
        stmt = stmt.order_by(Job.created_at.desc()).limit(limit)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_job(self, job_id: str, user_id: str) -> Job:
        """Get a specific job.

        Args:
            job_id: The job ID.
            user_id: The user's ID.

        Returns:
            The Job record.
        """
        stmt = select(Job).where(Job.id == job_id, Job.user_id == user_id)
        result = await self.db.execute(stmt)
        job = result.scalar_one_or_none()
        if not job:
            raise NotFoundException(f"Job '{job_id}' not found")
        return job

    async def toggle_saved(self, job_id: str, user_id: str) -> Job:
        """Toggle the saved/bookmark status of a job.

        Args:
            job_id: The job ID.
            user_id: The user's ID.

        Returns:
            Updated Job record.
        """
        job = await self.get_job(job_id, user_id)
        job.is_saved = not job.is_saved
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def mark_applied(self, job_id: str, user_id: str) -> Job:
        """Mark a job as applied.

        Args:
            job_id: The job ID.
            user_id: The user's ID.

        Returns:
            Updated Job record.
        """
        job = await self.get_job(job_id, user_id)
        job.is_applied = True
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def delete_job(self, job_id: str, user_id: str) -> None:
        """Delete a job listing.

        Args:
            job_id: The job ID.
            user_id: The user's ID.
        """
        job = await self.get_job(job_id, user_id)
        await self.db.delete(job)
        await self.db.commit()
