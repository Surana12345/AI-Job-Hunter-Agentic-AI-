"""
AI Job Hunter - Direct ATS Public Board Scraper Adapter
Fetches verified job openings directly from company career portals powered by:
- Greenhouse (https://boards-api.greenhouse.io/v1/boards/{company}/jobs)
- Lever (https://api.lever.co/v0/postings/{company})
- Ashby (https://api.ashbyhq.com/posting-api/job-board/{company})
"""

from __future__ import annotations

import httpx
from typing import List
from backend.jobs.schemas import JobSearchResult
from backend.utils.logger import get_logger

logger = get_logger("jobs.sources.ats_scrapers")

# Target top tech companies utilizing direct ATS boards
DEFAULT_TARGET_COMPANIES = {
    "greenhouse": ["figma", "stripe", "gitlab", "discord", "airtable", "datadog"],
    "lever": ["netflix", "palantir", "plaid", "retool", "postman"],
    "ashby": ["ramp", "linear", "openai", "perplexity", "replit"],
}


async def scrape_greenhouse_board(company_slug: str, query: str = "") -> List[JobSearchResult]:
    """Fetch jobs from public Greenhouse boards API."""
    url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs"
    results: List[JobSearchResult] = []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url)
            if res.status_code == 200:
                data = res.json()
                for job in data.get("jobs", []):
                    title = job.get("title", "")
                    if query and query.lower() not in title.lower() and query.lower() not in job.get("content", "").lower():
                        continue
                    loc = job.get("location", {}).get("name", "Remote")
                    results.append(
                        JobSearchResult(
                            title=title,
                            company=company_slug.capitalize(),
                            location=loc,
                            job_type="full-time",
                            description=job.get("content", f"Role at {company_slug.capitalize()}"),
                            url=job.get("absolute_url", f"https://boards.greenhouse.io/{company_slug}/jobs/{job.get('id')}"),
                            source="greenhouse_ats",
                            source_id=f"gh_{company_slug}_{job.get('id')}",
                        )
                    )
    except Exception as e:
        logger.debug("Greenhouse scrape error", company=company_slug, error=str(e))
    return results


async def scrape_lever_board(company_slug: str, query: str = "") -> List[JobSearchResult]:
    """Fetch jobs from public Lever postings API."""
    url = f"https://api.lever.co/v0/postings/{company_slug}?mode=json"
    results: List[JobSearchResult] = []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url)
            if res.status_code == 200:
                postings = res.json()
                for post in postings:
                    text = post.get("text", "")
                    if query and query.lower() not in text.lower():
                        continue
                    cat = post.get("categories", {})
                    results.append(
                        JobSearchResult(
                            title=text,
                            company=company_slug.capitalize(),
                            location=cat.get("location", "Remote"),
                            job_type=cat.get("commitment", "Full-time"),
                            description=post.get("descriptionPlain", "")[:1500],
                            url=post.get("hostedUrl", ""),
                            source="lever_ats",
                            source_id=f"lever_{company_slug}_{post.get('id')}",
                        )
                    )
    except Exception as e:
        logger.debug("Lever scrape error", company=company_slug, error=str(e))
    return results


async def scrape_direct_ats_boards(query: str = "", max_results: int = 15) -> List[JobSearchResult]:
    """Aggregate jobs across Greenhouse and Lever direct ATS endpoints."""
    all_jobs: List[JobSearchResult] = []

    # Sample top tech companies
    for comp in ["stripe", "figma", "datadog"]:
        gh_jobs = await scrape_greenhouse_board(comp, query)
        all_jobs.extend(gh_jobs)
        if len(all_jobs) >= max_results:
            break

    if len(all_jobs) < max_results:
        for comp in ["retool", "plaid", "postman"]:
            lv_jobs = await scrape_lever_board(comp, query)
            all_jobs.extend(lv_jobs)
            if len(all_jobs) >= max_results:
                break

    logger.info("Direct ATS board scrape complete", query=query, found=len(all_jobs))
    return all_jobs[:max_results]
