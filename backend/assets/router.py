"""
AI Job Hunter - Career Assets API Router

Endpoints for generating cover letters, recruiter messages, and interview prep guides.
"""

from __future__ import annotations

import json
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from backend.assets.schemas import (
    AssetListItem,
    CoverLetterRequest,
    CoverLetterResponse,
    InterviewPrepRequest,
    InterviewPrepResponse,
    PDFExportRequest,
    RecruiterMessageRequest,
    RecruiterMessageResponse,
)
from backend.assets.service import AssetService
from backend.dependencies import get_current_user, get_db
from backend.utils.pdf_generator import generate_application_pdf

router = APIRouter(prefix="/assets", tags=["Career Assets"])


@router.post(
    "/cover-letter",
    response_model=CoverLetterResponse,
    summary="Generate Cover Letter",
    description="Generate a tailored cover letter using Gemini AI agent.",
)
async def generate_cover_letter(
    request: CoverLetterRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CoverLetterResponse:
    service = AssetService(db)
    asset = await service.generate_cover_letter(
        user_id=current_user["sub"],
        resume_id=request.resume_id,
        job_description=request.job_description,
        job_title=request.job_title,
        company_name=request.company_name,
        hiring_manager_name=request.hiring_manager_name,
    )
    meta = asset.meta_info or {}
    return CoverLetterResponse(
        id=asset.id,
        job_title=meta.get("job_title", ""),
        company_name=meta.get("company_name", ""),
        cover_letter=asset.content,
        created_at=asset.created_at,
    )


@router.post(
    "/recruiter-message",
    response_model=RecruiterMessageResponse,
    summary="Generate Recruiter Message",
    description="Generate cold outreach message for LinkedIn/email.",
)
async def generate_recruiter_message(
    request: RecruiterMessageRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RecruiterMessageResponse:
    service = AssetService(db)
    asset = await service.generate_recruiter_message(
        user_id=current_user["sub"],
        resume_id=request.resume_id,
        job_title=request.job_title,
        company_name=request.company_name,
        recruiter_name=request.recruiter_name,
        platform=request.platform,
    )
    meta = asset.meta_info or {}
    return RecruiterMessageResponse(
        id=asset.id,
        platform=meta.get("platform", "LinkedIn"),
        subject=f"Application for {request.job_title} at {request.company_name}",
        message=asset.content,
        created_at=asset.created_at,
    )


@router.post(
    "/interview-prep",
    response_model=InterviewPrepResponse,
    summary="Generate Interview Prep Guide",
    description="Generate customized technical and behavioral interview preparation guide.",
)
async def generate_interview_prep(
    request: InterviewPrepRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InterviewPrepResponse:
    service = AssetService(db)
    asset = await service.generate_interview_prep(
        user_id=current_user["sub"],
        resume_id=request.resume_id,
        job_description=request.job_description,
        company_name=request.company_name,
        role_title=request.role_title,
    )
    data = json.loads(asset.content)
    return InterviewPrepResponse(
        id=asset.id,
        company_name=request.company_name,
        role_title=request.role_title,
        technical_questions=data.get("technical_questions", []),
        behavioral_questions=data.get("behavioral_questions", []),
        questions_to_ask_interviewer=data.get("questions_to_ask_interviewer", []),
        key_selling_points=data.get("key_selling_points", []),
        created_at=asset.created_at,
    )


@router.get(
    "/list",
    response_model=list[AssetListItem],
    summary="List generated assets",
)
async def list_assets(
    asset_type: str = Query("", description="Filter by asset type: cover_letter, recruiter_message, interview_prep"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[AssetListItem]:
    service = AssetService(db)
    assets = await service.list_assets(current_user["sub"], asset_type=asset_type)
    return [AssetListItem.model_validate(a) for a in assets]


@router.delete(
    "/{asset_id}",
    status_code=204,
    response_model=None,
    summary="Delete an asset",
)
async def delete_asset(
    asset_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AssetService(db)
    await service.delete_asset(asset_id, current_user["sub"])


@router.post(
    "/export-pdf",
    summary="Export application package as PDF",
    description="Generates a downloadable PDF dossier containing Cover Letter, Tailored Resume, Outreach Message, and Interview Guide.",
)
async def export_pdf(
    request: PDFExportRequest,
    current_user: dict = Depends(get_current_user),
) -> Response:
    user_name = current_user.get("full_name", "Candidate")
    pdf_bytes = generate_application_pdf(
        candidate_name=user_name,
        job_title=request.job_title,
        company_name=request.company_name,
        cover_letter=request.cover_letter or "",
        tailored_resume=request.tailored_resume or "",
        recruiter_message=request.recruiter_message or "",
        interview_prep=request.interview_prep,
    )
    safe_company = request.company_name.replace(" ", "_")
    filename = f"Application_Package_{safe_company}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

