"""
AI Job Hunter - Company Research Agent Node

LangGraph node that uses Gemini to research target companies and provide insights.
"""

from __future__ import annotations

import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.state import AgentState
from backend.config import get_settings
from backend.prompts.company_prompts import (
    COMPANY_RESEARCH_HUMAN,
    COMPANY_RESEARCH_SYSTEM,
)
from backend.utils.logger import get_logger

logger = get_logger("agents.company_research")


def _get_llm() -> ChatGoogleGenerativeAI:
    """Create a Gemini LLM instance for company research."""
    settings = get_settings()
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=0.3,
        convert_system_message_to_human=True,
    )


def _parse_json_response(text: str) -> dict:
    """Extract JSON from LLM response."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return json.loads(text)


async def company_research_node(state: AgentState) -> AgentState:
    """Research a target company.

    Reads: state['job_company'], state['job_title']
    Writes: state['company_info'], state['current_agent']
    """
    company_name = state.get("job_company", "")
    job_title = state.get("job_title", "")

    if not company_name:
        return {
            **state,
            "error": "Company name is required for company research",
            "current_agent": "company_research",
        }

    logger.info("Company research agent starting", company=company_name, role=job_title)

    try:
        settings = get_settings()
        if not settings.google_api_key or "your_gemini_api_key" in settings.google_api_key:
            logger.warning("Google API key not set, returning mock company research")
            return {
                **state,
                "company_info": {
                    "summary": f"{company_name} is a leading technology company delivering innovative enterprise solutions.",
                    "website": f"https://{company_name.lower().replace(' ', '')}.com",
                    "tech_stack": ["Python", "FastAPI", "React", "Cloud Native", "PostgreSQL"],
                    "products": ["Core Enterprise Platform", "Analytics Suite"],
                    "values": ["Innovation", "User Delight", "Operational Excellence"],
                    "interview_style": "Standard multi-stage technical and behavioral interviews.",
                    "recent_news": ["Expanding core engineering teams", "Investing in AI automation"],
                },
                "current_agent": "company_research",
                "error": None,
            }

        llm = _get_llm()

        messages = [
            SystemMessage(content=COMPANY_RESEARCH_SYSTEM),
            HumanMessage(
                content=COMPANY_RESEARCH_HUMAN.format(
                    company_name=company_name,
                    job_title=job_title or "Software Engineer",
                )
            ),
        ]

        response = await llm.ainvoke(messages)
        company_info = _parse_json_response(response.content)

        logger.info("Company research completed successfully", company=company_name)

        return {
            **state,
            "company_info": company_info,
            "current_agent": "company_research",
            "error": None,
        }

    except Exception as e:
        logger.warning("Company research agent failed, using fallback", error=str(e))
        return {
            **state,
            "company_info": {
                "summary": f"{company_name} is a major technology company.",
                "website": f"https://{company_name.lower().replace(' ', '')}.com",
                "tech_stack": ["Python", "React", "Cloud"],
                "products": ["Main Tech Solutions"],
                "values": ["Customer Focus", "Quality"],
                "interview_style": "Technical and cultural evaluation rounds.",
                "recent_news": ["Ongoing product innovation"],
            },
            "current_agent": "company_research",
            "error": None,
        }
