"""
AI Job Hunter - Interview Prep Agent Node

LangGraph node for generating interview preparation guides.
"""

from __future__ import annotations

import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.state import AgentState
from backend.config import get_settings
from backend.prompts.interview_prompts import (
    INTERVIEW_PREP_HUMAN,
    INTERVIEW_PREP_SYSTEM,
)
from backend.utils.logger import get_logger

logger = get_logger("agents.interview_prep")


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


async def interview_prep_node(state: AgentState) -> AgentState:
    logger.info("Interview prep agent starting")

    resume_text = state.get("resume_text", "")
    job_description = state.get("job_description", "")
    job_title = state.get("job_title", "Software Engineer")
    company_name = state.get("job_company", "Target Company")

    try:
        settings = get_settings()
        if not settings.google_api_key or "your_gemini_api_key" in settings.google_api_key:
            logger.warning("Google API key not set, returning fallback interview guide")
            return {
                **state,
                "interview_prep": {
                    "technical_questions": [
                        {
                            "question": f"How do your technical skills align with the core requirements for {job_title}?",
                            "suggested_answer": "Highlight core programming proficiency, system architecture experience, and past project impact.",
                            "key_concept": "Core Technical Alignment"
                        },
                        {
                            "question": "Describe your approach to designing scalable distributed backend services.",
                            "suggested_answer": "Discuss microservices, API caching, database indexing, and asynchronous messaging queues.",
                            "key_concept": "System Architecture & Scalability"
                        }
                    ],
                    "behavioral_questions": [
                        {
                            "question": "Describe a difficult technical bug or outage you resolved under tight deadlines.",
                            "star_guide": "Situation: System error; Task: Identify root cause; Action: Debugged logs & patched; Result: Restored 100% service stability."
                        }
                    ],
                    "questions_to_ask_interviewer": [
                        f"What are the highest priority technical goals for the engineering team at {company_name} over the next quarter?",
                        "How does the team foster technical growth and code quality standards?"
                    ],
                    "key_selling_points": [
                        "Strong experience in Python backend development and API design",
                        "Proven ability to collaborate across functional product teams"
                    ]
                },
                "current_agent": "interview_prep",
                "error": None,
            }

        llm = _get_llm()
        messages = [
            SystemMessage(content=INTERVIEW_PREP_SYSTEM),
            HumanMessage(
                content=INTERVIEW_PREP_HUMAN.format(
                    job_title=job_title,
                    company_name=company_name,
                    resume_text=resume_text[:2000],
                    job_description=job_description[:2000],
                )
            ),
        ]

        response = await llm.ainvoke(messages)
        res_data = _parse_json_response(response.content)

        return {
            **state,
            "interview_prep": res_data,
            "current_agent": "interview_prep",
            "error": None,
        }

    except Exception as e:
        logger.warning("Interview prep generation error, using fallback", error=str(e))
        return {
            **state,
            "interview_prep": {
                "technical_questions": [
                    {
                        "question": "Tell me about your technical background.",
                        "suggested_answer": "Summarize relevant experience.",
                        "key_concept": "Overview"
                    }
                ],
                "behavioral_questions": [],
                "questions_to_ask_interviewer": ["What is the team structure?"],
                "key_selling_points": ["Strong problem solving"]
            },
            "current_agent": "interview_prep",
            "error": None,
        }
