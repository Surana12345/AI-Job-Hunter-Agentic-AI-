"""
AI Job Hunter - Remotive Job Source Adapter

Fetches remote job listings from the Remotive API (free, no auth required).
Docs: https://remotive.com/api/remote-jobs
"""

from __future__ import annotations

import httpx

from backend.jobs.schemas import JobSearchResult
from backend.utils.logger import get_logger

logger = get_logger("jobs.sources.remotive")

REMOTIVE_API_URL = "https://remotive.com/api/remote-jobs"


async def search_remotive(
    query: str,
    max_results: int = 20,
    category: str = "",
) -> list[JobSearchResult]:
    """Search for remote jobs using the Remotive API.

    Args:
        query: Job search query.
        max_results: Maximum results to return.
        category: Remotive category (e.g. 'software-dev', 'data', 'devops').

    Returns:
        List of JobSearchResult objects.
    """
    params = {"search": query, "limit": max_results}
    if category:
        params["category"] = category

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(REMOTIVE_API_URL, params=params)
            response.raise_for_status()
            data = response.json()

        results = []
        for item in data.get("jobs", [])[:max_results]:
            # Clean HTML from description
            desc = item.get("description", "")
            # Simple HTML tag stripping
            import re
            desc_clean = re.sub(r"<[^>]+>", " ", desc)
            desc_clean = re.sub(r"\s+", " ", desc_clean).strip()
            # Truncate to reasonable length
            if len(desc_clean) > 2000:
                desc_clean = desc_clean[:2000] + "..."

            results.append(
                JobSearchResult(
                    title=item.get("title", "").strip(),
                    company=item.get("company_name", "Unknown"),
                    location=item.get("candidate_required_location", "Remote"),
                    job_type=item.get("job_type", ""),
                    description=desc_clean,
                    url=item.get("url", ""),
                    source="remotive",
                    source_id=str(item.get("id", "")),
                )
            )

        logger.info("Remotive search complete", query=query, results=len(results))
        return results

    except httpx.HTTPStatusError as e:
        logger.error("Remotive API error", status=e.response.status_code)
        return []
    except Exception as e:
        logger.error("Remotive search failed", error=str(e))
        return []
