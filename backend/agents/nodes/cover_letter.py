"""
AI Job Hunter - Cover Letter Agent Node

LangGraph node for generating tailored cover letters.
"""

from __future__ import annotations

import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.state import AgentState
from backend.config import get_settings
from backend.prompts.cover_letter_prompts import (
    COVER_LETTER_HUMAN,
    COVER_LETTER_SYSTEM,
)
from backend.utils.logger import get_logger

logger = get_logger("agents.cover_letter")


def _get_llm() -> ChatGoogleGenerativeAI:
    settings = get_settings()
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=0.3,
        convert_system_message_to_human=True,
    )


def _parse_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return json.loads(text)


async def cover_letter_node(state: AgentState) -> AgentState:
    logger.info("Cover letter agent starting")

    resume_text = state.get("resume_text", "")
    job_description = state.get("job_description", "")
    job_title = state.get("job_title", "Software Engineer")
    company_name = state.get("job_company", "Target Company")

    try:
        settings = get_settings()
        if not settings.google_api_key or "your_gemini_api_key" in settings.google_api_key:
            logger.warning("Google API key not set, returning template cover letter")
            fallback_letter = (
                f"Dear Hiring Team at {company_name},\n\n"
                f"I am writing to express my strong interest in the {job_title} position. "
                f"With extensive experience in software development and proven technical skills, "
                f"I am confident in my ability to make an immediate impact at {company_name}.\n\n"
                f"In my previous roles, I successfully delivered scalable applications and collaborated with cross-functional teams "
                f"to achieve strategic goals. My technical background aligns closely with the requirements specified in your job description.\n\n"
                f"Thank you for your time and consideration. I look forward to the opportunity to discuss how my experience and passion "
                f"for technical excellence make me a great fit for {company_name}.\n\n"
                f"Sincerely,\nCandidate"
            )
            return {
                **state,
                "cover_letter": fallback_letter,
                "current_agent": "cover_letter",
                "error": None,
            }

        llm = _get_llm()
        messages = [
            SystemMessage(content=COVER_LETTER_SYSTEM),
            HumanMessage(
                content=COVER_LETTER_HUMAN.format(
                    resume_text=resume_text[:2000],
                    job_title=job_title,
                    company_name=company_name,
                    hiring_manager_name="Hiring Manager",
                    job_description=job_description[:2000],
                )
            ),
        ]

        response = await llm.ainvoke(messages)
        res_data = _parse_json_response(response.content)

        return {
            **state,
            "cover_letter": res_data.get("cover_letter", ""),
            "current_agent": "cover_letter",
            "error": None,
        }

    except Exception as e:
        logger.warning("Cover letter generation error, using fallback", error=str(e))
        fallback_letter = (
            f"Dear Hiring Manager at {company_name},\n\n"
            f"I am thrilled to apply for the {job_title} role. My technical background and passion for building high-impact products "
            f"make me an ideal candidate for {company_name}.\n\n"
            f"Best regards,\nCandidate"
        )
        return {
            **state,
            "cover_letter": fallback_letter,
            "current_agent": "cover_letter",
            "error": None,
        }
