"""
AI Job Hunter - Mock Interview Agent Node

LangGraph node for real-time interactive mock interview evaluation and question generation.
"""

from __future__ import annotations

import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.state import AgentState
from backend.config import get_settings
from backend.prompts.mock_interview_prompts import (
    MOCK_INTERVIEW_HUMAN,
    MOCK_INTERVIEW_SYSTEM,
)
from backend.utils.logger import get_logger

logger = get_logger("agents.mock_interview")


def _get_llm() -> ChatGoogleGenerativeAI:
    settings = get_settings()
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=0.4,
        convert_system_message_to_human=True,
    )


def _parse_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return json.loads(text)


async def mock_interview_node(state: AgentState) -> AgentState:
    logger.info("Mock interview agent starting")

    question = state.get("interview_question", "Tell me about yourself and your technical experience.")
    user_answer = state.get("candidate_answer", "")
    job_title = state.get("job_title", "Software Engineer")
    company_name = state.get("job_company", "Target Company")

    try:
        settings = get_settings()
        if not settings.google_api_key or "your_gemini_api_key" in settings.google_api_key:
            logger.warning("Google API key not set, returning mock evaluation")
            return {
                **state,
                "interview_evaluation": {
                    "score": 8,
                    "feedback": "Good structured answer! You highlighted key technical skills and relevant project experience.",
                    "improved_answer": "To make it even stronger, quantify your impact (e.g. improved API response time by 45%).",
                    "next_question": f"How would you approach designing a scalable microservices architecture for {company_name}?",
                },
                "current_agent": "mock_interview",
                "error": None,
            }

        llm = _get_llm()
        messages = [
            SystemMessage(
                content=MOCK_INTERVIEW_SYSTEM.format(
                    job_title=job_title,
                    company_name=company_name,
                )
            ),
            HumanMessage(
                content=MOCK_INTERVIEW_HUMAN.format(
                    question=question,
                    user_answer=user_answer,
                )
            ),
        ]

        response = await llm.ainvoke(messages)
        res_data = _parse_json_response(response.content)

        return {
            **state,
            "interview_evaluation": res_data,
            "current_agent": "mock_interview",
            "error": None,
        }

    except Exception as e:
        logger.warning("Mock interview evaluation failed, using fallback", error=str(e))
        return {
            **state,
            "interview_evaluation": {
                "score": 7,
                "feedback": "Solid response. Keep practicing system design and STAR framework answers.",
                "improved_answer": "Focus on clear problem definition and quantified results.",
                "next_question": "Tell me about a time you had to deal with ambiguous requirements.",
            },
            "current_agent": "mock_interview",
            "error": None,
        }
