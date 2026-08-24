"""
CareerOps - Application Agent Node

Auto-maps form fields from candidate canonical profile, generates tailored answers
for application questions, and enforces automation policies.
"""

from __future__ import annotations

import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.state import AgentState
from backend.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger("agents.application_agent")

APPLICATION_FORM_SYSTEM = """You are an Application Automation Assistant.
Given a candidate's canonical profile and target job description, generate tailored form answers for custom application questions.

Return ONLY a valid JSON object matching:
{
    "mapped_fields": {
        "full_name": "Candidate Full Name",
        "email": "candidate@example.com",
        "phone": "+1 555-019-2831",
        "location": "San Francisco, CA",
        "work_authorization": "Authorized to work in US",
        "years_experience": 5
    },
    "custom_answers": [
        {
            "question": "Why do you want to join our engineering team?",
            "answer": "Tailored 2-3 sentence answer matching candidate experience with company mission."
        }
    ],
    "validation_passed": true,
    "submission_status": "PREPARED_FOR_REVIEW"
}
"""


async def application_agent_node(state: AgentState) -> AgentState:
    logger.info("Executing Application Agent node")
    profile = state.get("canonical_profile", {})
    job_title = state.get("job_title", "")
    job_company = state.get("job_company", "")

    settings = get_settings()

    if not settings.google_api_key or "your_gemini_api_key" in settings.google_api_key:
        fallback_app = {
            "mapped_fields": {
                "full_name": profile.get("name", "Candidate"),
                "email": "candidate@example.com",
                "years_experience": 5,
                "location": "Remote"
            },
            "custom_answers": [
                {
                    "question": f"Why are you excited about the {job_title} role at {job_company}?",
                    "answer": f"My background in software engineering and AI agents directly aligns with {job_company}'s tech stack."
                }
            ],
            "validation_passed": True,
            "submission_status": "PREPARED_FOR_REVIEW"
        }
        return {**state, "application_package": fallback_app, "current_agent": "application_agent", "error": None}

    try:
        llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.google_api_key,
            temperature=0.2
        )
        response = await llm.ainvoke([
            SystemMessage(content=APPLICATION_FORM_SYSTEM),
            HumanMessage(content=f"Candidate Profile:\n{json.dumps(profile)}\n\nJob: {job_title} at {job_company}")
        ])

        res_text = response.content.strip()
        if res_text.startswith("```"):
            lines = [l for l in res_text.split("\n") if not l.strip().startswith("```")]
            res_text = "\n".join(lines)

        app_pkg = json.loads(res_text)
        return {**state, "application_package": app_pkg, "current_agent": "application_agent", "error": None}
    except Exception as e:
        logger.error("Failed to generate application package", error=str(e))
        return {**state, "application_package": {}, "current_agent": "application_agent", "error": str(e)}
