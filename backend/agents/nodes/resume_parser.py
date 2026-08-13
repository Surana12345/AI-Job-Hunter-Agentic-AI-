"""
AI Job Hunter - Resume Parser Agent Node

LangGraph node that uses Gemini to parse raw resume text into
structured data (skills, experience, education, etc.).
"""

from __future__ import annotations

import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.state import AgentState, ResumeData
from backend.config import get_settings
from backend.prompts.resume_prompts import (
    RESUME_PARSER_HUMAN,
    RESUME_PARSER_SYSTEM,
    RESUME_SKILLS_EXTRACTION_HUMAN,
    RESUME_SKILLS_EXTRACTION_SYSTEM,
)
from backend.utils.logger import get_logger

logger = get_logger("agents.resume_parser")


def _get_llm() -> ChatGoogleGenerativeAI:
    """Create a Gemini LLM instance configured for JSON output."""
    settings = get_settings()
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=0.1,
        convert_system_message_to_human=True,
    )


def _parse_json_response(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown code blocks."""
    text = text.strip()
    # Remove markdown code blocks if present
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```json) and last line (```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return json.loads(text)


async def resume_parser_node(state: AgentState) -> AgentState:
    """Parse raw resume text into structured data using Gemini.

    Reads: state['resume_text']
    Writes: state['resume_data'], state['resume_skills'], state['current_agent']

    Args:
        state: The shared agent state.

    Returns:
        Updated agent state with parsed resume data.
    """
    logger.info("Resume parser agent starting", user_id=state.get("user_id"))

    resume_text = state.get("resume_text", "")
    if not resume_text:
        return {
            **state,
            "error": "No resume text provided",
            "current_agent": "resume_parser",
        }

    try:
        llm = _get_llm()

        # Step 1: Parse resume structure
        parse_messages = [
            SystemMessage(content=RESUME_PARSER_SYSTEM),
            HumanMessage(content=RESUME_PARSER_HUMAN.format(resume_text=resume_text)),
        ]

        parse_response = await llm.ainvoke(parse_messages)
        resume_data: ResumeData = _parse_json_response(parse_response.content)

        # Step 2: Extract detailed skills
        skills_messages = [
            SystemMessage(content=RESUME_SKILLS_EXTRACTION_SYSTEM),
            HumanMessage(
                content=RESUME_SKILLS_EXTRACTION_HUMAN.format(resume_text=resume_text)
            ),
        ]

        skills_response = await llm.ainvoke(skills_messages)
        skills_data = _parse_json_response(skills_response.content)

        # Merge skills into a flat list
        all_skills = skills_data.get("all_skills", [])
        if not all_skills:
            # Fallback: combine all skill categories
            for key, value in skills_data.items():
                if isinstance(value, list):
                    all_skills.extend(value)
            all_skills = list(set(all_skills))

        logger.info(
            "Resume parsed successfully",
            skills_count=len(all_skills),
            experience_count=len(resume_data.get("experience", [])),
        )

        return {
            **state,
            "resume_data": resume_data,
            "resume_skills": all_skills,
            "current_agent": "resume_parser",
            "error": None,
        }

    except json.JSONDecodeError as e:
        logger.error("Failed to parse LLM JSON response", error=str(e))
        return {
            **state,
            "error": f"Failed to parse resume: JSON decode error - {e}",
            "current_agent": "resume_parser",
        }
    except Exception as e:
        logger.error("Resume parser agent failed", error=str(e))
        return {
            **state,
            "error": f"Resume parser failed: {e}",
            "current_agent": "resume_parser",
        }
