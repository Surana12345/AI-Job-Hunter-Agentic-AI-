"""
AI Job Hunter - Application Tracker Service

Business logic for tracking job applications and computing metrics.
"""

from __future__ import annotations

from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.tracker.models import ApplicationTrack
from backend.tracker.schemas import (
    AnalyticsSummary,
    ApplicationTrackCreate,
    ApplicationTrackUpdate,
)
from backend.utils.exceptions import NotFoundException
from backend.utils.helpers import generate_id
from backend.utils.logger import get_logger

logger = get_logger("tracker.service")


class TrackerService:
    """Service layer for job application tracking & metrics."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_track(self, user_id: str, data: ApplicationTrackCreate) -> ApplicationTrack:
        applied_dt = datetime.utcnow() if data.status == "applied" else None

        track = ApplicationTrack(
            id=generate_id(),
            user_id=user_id,
            job_id=data.job_id,
            job_title=data.job_title,
            company_name=data.company_name,
            location=data.location,
            status=data.status,
            notes=data.notes,
            contact_person=data.contact_person,
            applied_date=applied_dt,
        )
        self.db.add(track)
        await self.db.commit()
        await self.db.refresh(track)
        logger.info("Created application track", track_id=track.id, company=data.company_name)
        return track

    async def update_track(
        self, track_id: str, user_id: str, data: ApplicationTrackUpdate
    ) -> ApplicationTrack:
        track = await self.get_track(track_id, user_id)

        if data.status is not None:
            # Set applied_date automatically if transitioning to 'applied' for first time
            if data.status == "applied" and not track.applied_date:
                track.applied_date = datetime.utcnow()
            track.status = data.status

        if data.notes is not None:
            track.notes = data.notes
        if data.applied_date is not None:
            track.applied_date = data.applied_date
        if data.follow_up_date is not None:
            track.follow_up_date = data.follow_up_date
        if data.contact_person is not None:
            track.contact_person = data.contact_person
        if data.salary_offered is not None:
            track.salary_offered = data.salary_offered

        await self.db.commit()
        await self.db.refresh(track)
        return track

    async def list_tracks(
        self, user_id: str, status: str = ""
    ) -> list[ApplicationTrack]:
        stmt = select(ApplicationTrack).where(ApplicationTrack.user_id == user_id)
        if status:
            stmt = stmt.where(ApplicationTrack.status == status)
        stmt = stmt.order_by(ApplicationTrack.updated_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_track(self, track_id: str, user_id: str) -> ApplicationTrack:
        stmt = select(ApplicationTrack).where(
            ApplicationTrack.id == track_id, ApplicationTrack.user_id == user_id
        )
        res = await self.db.execute(stmt)
        track = res.scalar_one_or_none()
        if not track:
            raise NotFoundException(f"Application track '{track_id}' not found")
        return track

    async def delete_track(self, track_id: str, user_id: str) -> None:
        track = await self.get_track(track_id, user_id)
        await self.db.delete(track)
        await self.db.commit()

    async def get_analytics(self, user_id: str) -> AnalyticsSummary:
        tracks = await self.list_tracks(user_id)

        counts = {
            "saved": 0,
            "applied": 0,
            "interview": 0,
            "offer": 0,
            "rejected": 0,
        }

        for t in tracks:
            st = (t.status or "saved").lower()
            if st in counts:
                counts[st] += 1

        total = len(tracks)
        applied_total = counts["applied"] + counts["interview"] + counts["offer"] + counts["rejected"]
        denom = max(applied_total, 1)

        interview_rate = round(((counts["interview"] + counts["offer"]) / denom) * 100, 1)
        offer_rate = round((counts["offer"] / denom) * 100, 1)

        return AnalyticsSummary(
            total_tracked=total,
            saved_count=counts["saved"],
            applied_count=counts["applied"],
            interview_count=counts["interview"],
            offer_count=counts["offer"],
            rejected_count=counts["rejected"],
            interview_rate=interview_rate,
            offer_rate=offer_rate,
        )
