"""
AI Job Hunter - Resume API Router

Endpoints for resume upload, parsing, listing, ATS analysis, and management.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from backend.dependencies import get_current_user, get_db
from backend.resume.schemas import (
    ATSAnalysisRequest,
    ATSAnalysisResponse,
    ResumeListItem,
    ResumeResponse,
    ResumeUploadResponse,
)
from backend.resume.service import ResumeService

router = APIRouter(prefix="/resume", tags=["Resume"])


@router.post(
    "/upload",
    response_model=ResumeUploadResponse,
    status_code=201,
    summary="Upload a resume",
    description="Upload a PDF or DOCX resume file. Text is extracted automatically.",
)
async def upload_resume(
    file: UploadFile = File(..., description="Resume file (PDF or DOCX)"),
    is_primary: bool = Query(False, description="Set as primary resume"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResumeUploadResponse:
    service = ResumeService(db)
    resume = await service.upload_resume(
        user_id=current_user["sub"],
        file=file,
        is_primary=is_primary,
    )
    return ResumeUploadResponse.model_validate(resume)


@router.post(
    "/{resume_id}/parse",
    response_model=ResumeResponse,
    summary="Parse a resume with AI",
    description="Run LLM-powered parsing to extract structured data (skills, experience, education).",
)
async def parse_resume(
    resume_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResumeResponse:
    service = ResumeService(db)
    resume = await service.parse_resume(resume_id, current_user["sub"])
    return ResumeResponse.model_validate(resume)


@router.post(
    "/analyze-ats",
    response_model=ATSAnalysisResponse,
    summary="Analyze ATS compatibility",
    description="Compare a resume against a job description for ATS compatibility scoring.",
)
async def analyze_ats(
    request: ATSAnalysisRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ATSAnalysisResponse:
    service = ResumeService(db)
    result = await service.analyze_ats(
        resume_id=request.resume_id,
        user_id=current_user["sub"],
        job_description=request.job_description,
        job_title=request.job_title or "",
        job_company=request.job_company or "",
    )
    return ATSAnalysisResponse(**result)


@router.get(
    "/list",
    response_model=list[ResumeListItem],
    summary="List all resumes",
    description="Get all resumes uploaded by the current user.",
)
async def list_resumes(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ResumeListItem]:
    service = ResumeService(db)
    resumes = await service.list_resumes(current_user["sub"])
    items = []
    for r in resumes:
        items.append(
            ResumeListItem(
                id=r.id,
                filename=r.filename,
                file_type=r.file_type,
                is_primary=r.is_primary,
                skills_count=len(r.skills) if r.skills else 0,
                created_at=r.created_at,
            )
        )
    return items


@router.get(
    "/{resume_id}",
    response_model=ResumeResponse,
    summary="Get resume details",
    description="Get full details of a specific resume including parsed data.",
)
async def get_resume(
    resume_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResumeResponse:
    service = ResumeService(db)
    resume = await service.get_resume(resume_id, current_user["sub"])
    return ResumeResponse.model_validate(resume)


@router.put(
    "/{resume_id}/set-primary",
    response_model=ResumeResponse,
    summary="Set as primary resume",
    description="Set this resume as the primary/active resume for job applications.",
)
async def set_primary(
    resume_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResumeResponse:
    service = ResumeService(db)
    resume = await service.set_primary(resume_id, current_user["sub"])
    return ResumeResponse.model_validate(resume)


@router.delete(
    "/{resume_id}",
    status_code=204,
    summary="Delete a resume",
    description="Delete a resume and its associated file from disk.",
    response_model=None,
)
async def delete_resume(
    resume_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    await service.delete_resume(resume_id, current_user["sub"])

