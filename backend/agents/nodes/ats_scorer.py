"""
AI Job Hunter - ATS Scorer Agent Node

LangGraph node that uses Gemini to analyze ATS compatibility
between a resume and a job description.
"""

from __future__ import annotations

import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.state import AgentState, ATSResult
from backend.config import get_settings
from backend.prompts.ats_prompts import (
    ATS_KEYWORD_EXTRACTION_HUMAN,
    ATS_KEYWORD_EXTRACTION_SYSTEM,
    ATS_SCORER_HUMAN,
    ATS_SCORER_SYSTEM,
)
from backend.utils.logger import get_logger

logger = get_logger("agents.ats_scorer")


def _get_llm() -> ChatGoogleGenerativeAI:
    """Create a Gemini LLM instance configured for JSON output."""
    settings = get_settings()
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=0.2,
        convert_system_message_to_human=True,
    )


def _parse_json_response(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown code blocks."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return json.loads(text)


async def extract_job_keywords(job_description: str) -> dict:
    """Extract keywords and requirements from a job description.

    Args:
        job_description: The full job description text.

    Returns:
        Dict with required_skills, preferred_skills, important_keywords, etc.
    """
    llm = _get_llm()

    messages = [
        SystemMessage(content=ATS_KEYWORD_EXTRACTION_SYSTEM),
        HumanMessage(
            content=ATS_KEYWORD_EXTRACTION_HUMAN.format(job_description=job_description)
        ),
    ]

    response = await llm.ainvoke(messages)
    return _parse_json_response(response.content)


async def ats_scorer_node(state: AgentState) -> AgentState:
    """Analyze ATS compatibility between resume and job description.

    Reads: state['resume_text'], state['job_description']
    Writes: state['ats_result'], state['job_keywords'], state['current_agent']

    Args:
        state: The shared agent state.

    Returns:
        Updated agent state with ATS analysis results.
    """
    logger.info("ATS scorer agent starting", user_id=state.get("user_id"))

    resume_text = state.get("resume_text", "")
    job_description = state.get("job_description", "")

    if not resume_text:
        return {
            **state,
            "error": "No resume text provided for ATS analysis",
            "current_agent": "ats_scorer",
        }

    if not job_description:
        return {
            **state,
            "error": "No job description provided for ATS analysis",
            "current_agent": "ats_scorer",
        }

    try:
        llm = _get_llm()

        # Step 1: Extract job keywords
        keywords_data = await extract_job_keywords(job_description)
        job_keywords = keywords_data.get("important_keywords", [])

        # Step 2: Run ATS analysis
        ats_messages = [
            SystemMessage(content=ATS_SCORER_SYSTEM),
            HumanMessage(
                content=ATS_SCORER_HUMAN.format(
                    resume_text=resume_text,
                    job_description=job_description,
                )
            ),
        ]

        ats_response = await llm.ainvoke(ats_messages)
        ats_result: ATSResult = _parse_json_response(ats_response.content)

        logger.info(
            "ATS analysis complete",
            overall_score=ats_result.get("overall_score"),
            matched_skills=len(ats_result.get("matched_skills", [])),
            missing_skills=len(ats_result.get("missing_skills", [])),
        )

        return {
            **state,
            "ats_result": ats_result,
            "job_keywords": job_keywords,
            "current_agent": "ats_scorer",
            "error": None,
        }

    except json.JSONDecodeError as e:
        logger.error("Failed to parse ATS JSON response", error=str(e))
        return {
            **state,
            "error": f"ATS analysis failed: JSON decode error - {e}",
            "current_agent": "ats_scorer",
        }
    except Exception as e:
        logger.error("ATS scorer agent failed", error=str(e))
        return {
            **state,
            "error": f"ATS analysis failed: {e}",
            "current_agent": "ats_scorer",
        }
