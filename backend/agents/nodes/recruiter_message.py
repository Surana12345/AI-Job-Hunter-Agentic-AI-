"""
AI Job Hunter - Recruiter Outreach Agent Node

LangGraph node for generating personalized recruiter outreach messages.
"""

from __future__ import annotations

import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.state import AgentState
from backend.config import get_settings
from backend.prompts.recruiter_prompts import (
    RECRUITER_MESSAGE_HUMAN,
    RECRUITER_MESSAGE_SYSTEM,
)
from backend.utils.logger import get_logger

logger = get_logger("agents.recruiter_message")


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


async def recruiter_message_node(state: AgentState) -> AgentState:
    logger.info("Recruiter message agent starting")

    resume_text = state.get("resume_text", "")
    job_title = state.get("job_title", "Software Engineer")
    company_name = state.get("job_company", "Target Company")
    platform = state.get("outreach_platform", "LinkedIn")

    try:
        settings = get_settings()
        if not settings.google_api_key or "your_gemini_api_key" in settings.google_api_key:
            logger.warning("Google API key not set, returning fallback message")
            return {
                **state,
                "recruiter_message": (
                    f"Hi team,\n\nI noticed the {job_title} opening at {company_name} and wanted to reach out directly. "
                    f"My background in software engineering aligns very closely with your technical stack. "
                    f"Would you be open to a quick 5-minute chat this week?"
                ),
                "current_agent": "recruiter_message",
                "error": None,
            }

        llm = _get_llm()
        messages = [
            SystemMessage(content=RECRUITER_MESSAGE_SYSTEM),
            HumanMessage(
                content=RECRUITER_MESSAGE_HUMAN.format(
                    platform=platform,
                    resume_text=resume_text[:1500],
                    job_title=job_title,
                    company_name=company_name,
                    recruiter_name="Recruiter",
                )
            ),
        ]

        response = await llm.ainvoke(messages)
        res_data = _parse_json_response(response.content)

        return {
            **state,
            "recruiter_message": res_data.get("message", ""),
            "current_agent": "recruiter_message",
            "error": None,
        }

    except Exception as e:
        logger.warning("Recruiter message generation error, using fallback", error=str(e))
        return {
            **state,
            "recruiter_message": (
                f"Hi,\n\nI'm very interested in the {job_title} role at {company_name}. "
                f"I'd love to connect and share how my technical experience can add value to your team."
            ),
            "current_agent": "recruiter_message",
            "error": None,
        }
