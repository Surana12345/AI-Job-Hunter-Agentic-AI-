"""
AI Job Hunter - Job Discovery Agent Node

LangGraph node for automated job discovery using search tools.
"""

from __future__ import annotations

from backend.agents.state import AgentState
from backend.jobs.sources.remotive import search_remotive
from backend.utils.logger import get_logger

logger = get_logger("agents.job_discovery")


async def job_discovery_node(state: AgentState) -> AgentState:
    """Discover relevant job listings based on candidate profile / skills or query.

    Reads: state['resume_skills'], state['job_title']
    Writes: state['discovered_jobs'], state['current_agent']
    """
    logger.info("Job discovery agent starting")

    query = state.get("job_title") or "Software Engineer"
    skills = state.get("resume_skills") or []
    if skills and not state.get("job_title"):
        query = f"{skills[0]} Developer"

    try:
        results = await search_remotive(query=query, max_results=10)

        job_dicts = [
            {
                "title": r.title,
                "company": r.company,
                "location": r.location,
                "description": r.description[:300] + "...",
                "url": r.url,
                "source": r.source,
            }
            for r in results
        ]

        logger.info("Job discovery completed", count=len(job_dicts))

        return {
            **state,
            "discovered_jobs": job_dicts,
            "current_agent": "job_discovery",
            "error": None,
        }

    except Exception as e:
        logger.error("Job discovery agent failed", error=str(e))
        return {
            **state,
            "error": f"Job discovery failed: {e}",
            "current_agent": "job_discovery",
        }
