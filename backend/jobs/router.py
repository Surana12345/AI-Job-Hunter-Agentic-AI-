"""
AI Job Hunter - Jobs API Router

Endpoints for job search, listing, bookmarking, and management.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.dependencies import get_current_user, get_db
from backend.jobs.schemas import (
    CompanyResearchRequest,
    CompanyResearchResponse,
    JobListItem,
    JobResponse,
    JobSearchRequest,
)
from backend.jobs.service import JobService

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post(
    "/search",
    response_model=list[JobListItem],
    summary="Search for jobs",
    description="Search across Remotive and Adzuna APIs. Results are saved for later review.",
)
async def search_jobs(
    request: JobSearchRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[JobListItem]:
    service = JobService(db)
    jobs = await service.search_jobs(
        user_id=current_user["sub"],
        query=request.query,
        location=request.location,
        job_type=request.job_type,
        max_results=request.max_results,
    )
    return [JobListItem.model_validate(j) for j in jobs]


@router.get(
    "/list",
    response_model=list[JobListItem],
    summary="List discovered jobs",
    description="Get all discovered jobs. Use saved_only=true for bookmarked jobs.",
)
async def list_jobs(
    saved_only: bool = Query(False, description="Only show saved jobs"),
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[JobListItem]:
    service = JobService(db)
    jobs = await service.list_jobs(current_user["sub"], saved_only=saved_only, limit=limit)
    return [JobListItem.model_validate(j) for j in jobs]


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get job details",
    description="Get full details of a specific job including description and company info.",
)
async def get_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    service = JobService(db)
    job = await service.get_job(job_id, current_user["sub"])
    return JobResponse.model_validate(job)


@router.put(
    "/{job_id}/toggle-saved",
    response_model=JobResponse,
    summary="Toggle saved status",
    description="Bookmark or unbookmark a job listing.",
)
async def toggle_saved(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    service = JobService(db)
    job = await service.toggle_saved(job_id, current_user["sub"])
    return JobResponse.model_validate(job)


@router.put(
    "/{job_id}/mark-applied",
    response_model=JobResponse,
    summary="Mark as applied",
    description="Mark a job as applied to track your application status.",
)
async def mark_applied(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    service = JobService(db)
    job = await service.mark_applied(job_id, current_user["sub"])
    return JobResponse.model_validate(job)


@router.post(
    "/research-company",
    response_model=CompanyResearchResponse,
    summary="Research a company",
    description="Use AI to research a company and gather insights for interview prep.",
)
async def research_company(
    request: CompanyResearchRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CompanyResearchResponse:
    from backend.agents.orchestrator import run_agent_pipeline

    result = await run_agent_pipeline(
        intent="research_company",
        state_overrides={
            "user_id": current_user["sub"],
            "job_company": request.company_name,
            "job_title": request.job_title,
        },
    )

    info = result.get("company_info", {})
    return CompanyResearchResponse(
        name=request.company_name,
        summary=info.get("summary", "Research not available yet"),
        website=info.get("website", ""),
        tech_stack=info.get("tech_stack", []),
        products=info.get("products", []),
        values=info.get("values", []),
        interview_style=info.get("interview_style", ""),
        recent_news=info.get("recent_news", []),
    )


@router.delete(
    "/{job_id}",
    status_code=204,
    summary="Delete a job",
    response_model=None,
)
async def delete_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = JobService(db)
    await service.delete_job(job_id, current_user["sub"])
