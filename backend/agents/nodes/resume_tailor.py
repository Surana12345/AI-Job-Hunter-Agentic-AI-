"""
AI Job Hunter - Resume Tailor Agent Node

LangGraph node that uses Gemini to tailor a resume for a specific
job description, optimizing for ATS compatibility.
"""

from __future__ import annotations

import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.state import AgentState
from backend.config import get_settings
from backend.prompts.tailor_prompts import (
    RESUME_TAILOR_HUMAN,
    RESUME_TAILOR_SYSTEM,
)
from backend.utils.logger import get_logger

logger = get_logger("agents.resume_tailor")


def _get_llm() -> ChatGoogleGenerativeAI:
    """Create a Gemini LLM instance for resume tailoring."""
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


async def resume_tailor_node(state: AgentState) -> AgentState:
    """Tailor a resume for a specific job description.

    Reads: state['resume_text'], state['job_description']
    Writes: state['tailored_resume'], state['current_agent']

    Args:
        state: The shared agent state.

    Returns:
        Updated agent state with tailored resume.
    """
    logger.info("Resume tailor agent starting", user_id=state.get("user_id"))

    resume_text = state.get("resume_text", "")
    job_description = state.get("job_description", "")

    if not resume_text or not job_description:
        return {
            **state,
            "error": "Both resume text and job description required for tailoring",
            "current_agent": "resume_tailor",
        }

    try:
        llm = _get_llm()

        messages = [
            SystemMessage(content=RESUME_TAILOR_SYSTEM),
            HumanMessage(
                content=RESUME_TAILOR_HUMAN.format(
                    resume_text=resume_text,
                    job_description=job_description,
                )
            ),
        ]

        response = await llm.ainvoke(messages)
        result = _parse_json_response(response.content)

        logger.info(
            "Resume tailored successfully",
            changes=len(result.get("changes_made", [])),
        )

        return {
            **state,
            "tailored_resume": result.get("tailored_resume", ""),
            "current_agent": "resume_tailor",
            "error": None,
        }

    except Exception as e:
        logger.error("Resume tailor agent failed", error=str(e))
        return {
            **state,
            "error": f"Resume tailoring failed: {e}",
            "current_agent": "resume_tailor",
        }
