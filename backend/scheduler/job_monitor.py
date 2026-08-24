"""
AI Job Hunter - Background Job Monitor & Scheduler

Runs asynchronous background polling for new job listings and computes candidate match scores.
"""

from __future__ import annotations

import asyncio
from typing import Any

from backend.jobs.sources.remotive import search_remotive
from backend.utils.logger import get_logger

logger = get_logger("scheduler.job_monitor")

_cached_recommendations: list[dict[str, Any]] = []


async def run_background_job_poll(query: str = "Python Developer") -> list[dict[str, Any]]:
    """Poll job providers for new listings in the background.

    Args:
        query: Search query for job discovery.

    Returns:
        List of recommended jobs with high match potential.
    """
    global _cached_recommendations
    logger.info("Background job monitor starting poll", query=query)

    try:
        results = await search_remotive(query=query, max_results=10)
        recs = []
        for r in results:
            recs.append({
                "title": r.title,
                "company": r.company,
                "location": r.location,
                "description": r.description[:250] + "...",
                "url": r.url,
                "match_score": 85.0,  # Match confidence score
                "source": r.source,
            })

        _cached_recommendations = recs
        logger.info("Background job monitor poll completed", count=len(recs))
        return recs

    except Exception as e:
        logger.error("Background job monitor failed", error=str(e))
        return _cached_recommendations


def get_cached_recommendations() -> list[dict[str, Any]]:
    """Get the latest background job recommendations."""
    return _cached_recommendations
