"""
AI Job Hunter - Application Tracker API Router

Endpoints for tracking applications, updating status, and getting analytics.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.dependencies import get_current_user, get_db
from backend.tracker.schemas import (
    AnalyticsSummary,
    ApplicationTrackCreate,
    ApplicationTrackResponse,
    ApplicationTrackUpdate,
)
from backend.tracker.service import TrackerService

router = APIRouter(prefix="/tracker", tags=["Application Tracker"])


@router.post(
    "",
    response_model=ApplicationTrackResponse,
    status_code=201,
    summary="Track a job application",
)
async def create_track(
    request: ApplicationTrackCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApplicationTrackResponse:
    service = TrackerService(db)
    track = await service.create_track(current_user["sub"], request)
    return ApplicationTrackResponse.model_validate(track)


@router.get(
    "/analytics",
    response_model=AnalyticsSummary,
    summary="Get application conversion analytics",
)
async def get_analytics(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AnalyticsSummary:
    service = TrackerService(db)
    return await service.get_analytics(current_user["sub"])


@router.get(
    "/list",
    response_model=list[ApplicationTrackResponse],
    summary="List tracked applications",
)
async def list_tracks(
    status: str = Query("", description="Filter by status: saved, applied, interview, offer, rejected"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ApplicationTrackResponse]:
    service = TrackerService(db)
    tracks = await service.list_tracks(current_user["sub"], status=status)
    return [ApplicationTrackResponse.model_validate(t) for t in tracks]


@router.get(
    "/{track_id}",
    response_model=ApplicationTrackResponse,
    summary="Get tracked application details",
)
async def get_track(
    track_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApplicationTrackResponse:
    service = TrackerService(db)
    track = await service.get_track(track_id, current_user["sub"])
    return ApplicationTrackResponse.model_validate(track)


@router.patch(
    "/{track_id}",
    response_model=ApplicationTrackResponse,
    summary="Update tracked application",
)
async def update_track(
    track_id: str,
    request: ApplicationTrackUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApplicationTrackResponse:
    service = TrackerService(db)
    track = await service.update_track(track_id, current_user["sub"], request)
    return ApplicationTrackResponse.model_validate(track)


@router.delete(
    "/{track_id}",
    status_code=204,
    response_model=None,
    summary="Delete tracked application",
)
async def delete_track(
    track_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TrackerService(db)
    await service.delete_track(track_id, current_user["sub"])


@router.post(
    "/classify-inbound",
    summary="Classify inbound email and sync application status",
)
async def classify_inbound_email(
    payload: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from backend.tracker.email_classifier import InboundEmailClassifier
    email_text = payload.get("body", "")
    subject = payload.get("subject", "")
    sender = payload.get("sender", "")

    result = await InboundEmailClassifier.classify_email(
        email_text=email_text, subject=subject, sender=sender
    )
    return result

