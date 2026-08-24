"""
AI Job Hunter - Salary Negotiation Agent Node

LangGraph node for evaluating job offers and generating counter-offer scripts.
"""

from __future__ import annotations

import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.state import AgentState
from backend.config import get_settings
from backend.prompts.negotiation_prompts import (
    SALARY_NEGOTIATION_HUMAN,
    SALARY_NEGOTIATION_SYSTEM,
)
from backend.utils.logger import get_logger

logger = get_logger("agents.salary_negotiation")


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


async def salary_negotiation_node(state: AgentState) -> AgentState:
    logger.info("Salary negotiation agent starting")

    job_title = state.get("job_title", "Software Engineer")
    company_name = state.get("job_company", "Target Company")
    offered_base = int(state.get("offered_base", 140000))
    offered_bonus = int(state.get("offered_bonus", 15000))
    offered_equity = int(state.get("offered_equity", 20000))
    location = state.get("job_location", "Remote")
    target_counter = int(state.get("target_counter", offered_base * 1.15))
    notes = state.get("negotiation_notes", "")

    try:
        settings = get_settings()
        if not settings.google_api_key or "your_gemini_api_key" in settings.google_api_key:
            logger.warning("Google API key not set, returning fallback negotiation plan")
            return {
                **state,
                "negotiation_plan": {
                    "market_range": {
                        "percentile_25": int(offered_base * 0.95),
                        "percentile_50_median": int(offered_base * 1.1),
                        "percentile_75": int(offered_base * 1.25),
                    },
                    "offer_assessment": f"The offered base of ${offered_base:,} for {job_title} at {company_name} is competitive, but there is room for adjustment.",
                    "recommended_counter": int(offered_base * 1.12),
                    "counter_offer_script": (
                        f"Dear Hiring Team at {company_name},\n\n"
                        f"Thank you so much for extending the offer for the {job_title} position. "
                        f"I am thrilled about the prospect of joining {company_name} and contributing to your engineering goals.\n\n"
                        f"Based on my technical experience and current market benchmarks for {job_title} in {location}, "
                        f"I would like to explore if we can adjust the base salary to ${int(offered_base * 1.12):,}. "
                        f"I am confident this reflects the immediate value I will bring to the team.\n\n"
                        f"I look forward to discussing this and finalizing the agreement.\n\nSincerely,\nCandidate"
                    ),
                    "key_levers": [
                        "Emphasize specialized domain expertise and direct tech stack match",
                        "Inquire about performance bonuses or signing bonus flexibility",
                        "Request early 6-month performance review for compensation alignment"
                    ]
                },
                "current_agent": "salary_negotiation",
                "error": None,
            }

        llm = _get_llm()
        messages = [
            SystemMessage(
                content=SALARY_NEGOTIATION_SYSTEM.format(
                    job_title=job_title,
                    company_name=company_name,
                    offered_base=offered_base,
                    offered_bonus=offered_bonus,
                    offered_equity=offered_equity,
                    location=location,
                    target_counter=target_counter,
                )
            ),
            HumanMessage(
                content=SALARY_NEGOTIATION_HUMAN.format(
                    job_title=job_title,
                    company_name=company_name,
                    offered_base=offered_base,
                    offered_bonus=offered_bonus,
                    offered_equity=offered_equity,
                    location=location,
                    notes=notes or "None",
                )
            ),
        ]

        response = await llm.ainvoke(messages)
        res_data = _parse_json_response(response.content)

        return {
            **state,
            "negotiation_plan": res_data,
            "current_agent": "salary_negotiation",
            "error": None,
        }

    except Exception as e:
        logger.warning("Salary negotiation evaluation failed, using fallback", error=str(e))
        return {
            **state,
            "negotiation_plan": {
                "market_range": {
                    "percentile_25": offered_base,
                    "percentile_50_median": int(offered_base * 1.1),
                    "percentile_75": int(offered_base * 1.2),
                },
                "offer_assessment": "Solid offer. Consider negotiating base or sign-on bonus.",
                "recommended_counter": int(offered_base * 1.1),
                "counter_offer_script": f"Dear Hiring Team, Thank you for the offer for {job_title} at {company_name}...",
                "key_levers": ["Highlight key achievements", "Ask for signing bonus"],
            },
            "current_agent": "salary_negotiation",
            "error": None,
        }
