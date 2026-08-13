"""AI Job Hunter - Search Tools

Web search tools for agents to gather external information.
Placeholder for Phase 4 implementation.
"""

from __future__ import annotations

from typing import Any

from backend.utils.logger import get_logger

logger = get_logger("agents.tools.search")


async def search_web(query: str, num_results: int = 5) -> list[dict[str, Any]]:
    """Search the web for information.

    This will be implemented in Phase 4 with DuckDuckGo or SerpAPI integration.

    Args:
        query: Search query string.
        num_results: Number of results to return.

    Returns:
        List of search result dicts with title, url, snippet.
    """
    logger.info("Web search requested (placeholder)", query=query)
    return []


async def search_company_info(company_name: str) -> dict[str, Any]:
    """Search for company information.

    Will be fully implemented in Phase 4.

    Args:
        company_name: Name of the company to research.

    Returns:
        Dict with company information.
    """
    logger.info("Company search requested (placeholder)", company=company_name)
    return {
        "name": company_name,
        "info": "Company research will be available in Phase 4",
    }
