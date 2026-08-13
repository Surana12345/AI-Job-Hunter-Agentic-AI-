"""
AI Job Hunter - Adzuna Job Source Adapter

Fetches job listings from the Adzuna API (free tier: 250 req/month).
Docs: https://developer.adzuna.com/
"""

from __future__ import annotations

from typing import Any

import httpx

from backend.config import get_settings
from backend.jobs.schemas import JobSearchResult
from backend.utils.logger import get_logger

logger = get_logger("jobs.sources.adzuna")

ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs"


async def search_adzuna(
    query: str,
    location: str = "",
    max_results: int = 20,
    country: str = "us",
) -> list[JobSearchResult]:
    """Search for jobs using the Adzuna API.

    Args:
        query: Job search query (e.g. 'Python Developer').
        location: Location filter.
        max_results: Maximum results to return.
        country: Country code (us, gb, ca, au, etc.).

    Returns:
        List of JobSearchResult objects.
    """
    settings = get_settings()

    if not settings.adzuna_app_id or not settings.adzuna_api_key:
        logger.warning("Adzuna API credentials not configured, skipping")
        return []

    params: dict[str, Any] = {
        "app_id": settings.adzuna_app_id,
        "app_key": settings.adzuna_api_key,
        "results_per_page": min(max_results, 50),
        "what": query,
        "content-type": "application/json",
    }

    if location:
        params["where"] = location

    url = f"{ADZUNA_BASE_URL}/{country}/search/1"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        results = []
        for item in data.get("results", []):
            results.append(
                JobSearchResult(
                    title=item.get("title", "").strip(),
                    company=item.get("company", {}).get("display_name", "Unknown"),
                    location=item.get("location", {}).get("display_name", ""),
                    description=item.get("description", ""),
                    url=item.get("redirect_url", ""),
                    salary_min=item.get("salary_min"),
                    salary_max=item.get("salary_max"),
                    currency="USD" if country == "us" else "GBP",
                    source="adzuna",
                    source_id=str(item.get("id", "")),
                )
            )

        logger.info("Adzuna search complete", query=query, results=len(results))
        return results

    except httpx.HTTPStatusError as e:
        logger.error("Adzuna API error", status=e.response.status_code, detail=str(e))
        return []
    except Exception as e:
        logger.error("Adzuna search failed", error=str(e))
        return []
