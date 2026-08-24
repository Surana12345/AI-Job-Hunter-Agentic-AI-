"""
CareerOps - Profile Agent Node

Extracts structured canonical candidate profile JSON from raw resume text
and candidate preferences.
"""

from __future__ import annotations

import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.state import AgentState
from backend.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger("agents.profile_agent")

PROFILE_EXTRACTION_SYSTEM = """You are an expert Talent Intelligence AI.
Extract a canonical candidate profile from the provided resume text and user inputs.

Return ONLY a valid JSON object matching this schema:
{
    "name": "Candidate Full Name",
    "experience_level": "Entry Level" | "Mid Level" | "Senior Level" | "Lead / Staff",
    "education": {
        "degree": "B.S. Computer Science",
        "institution": "University Name",
        "year": 2022
    },
    "skills": ["Python", "FastAPI", "LangGraph", "Docker", "SQL"],
    "projects": [
        {
            "title": "Project Name",
            "description": "Short description of accomplishments",
            "technologies": ["Python", "Gemini API"]
        }
    ],
    "experience": [
        {
            "role": "Software Engineer",
            "company": "Tech Corp",
            "duration": "2022 - Present",
            "highlights": ["Built microservices", "Improved latency by 40%"]
        }
    ],
    "certifications": ["AWS Certified Solutions Architect"],
    "preferred_roles": ["Backend Engineer", "AI Engineer", "Software Engineer"],
    "locations": ["Remote", "San Francisco, CA"],
    "salary_expectation": {
        "currency": "USD",
        "min_base": 130000,
        "target_base": 150000
    }
}
"""


async def profile_agent_node(state: AgentState) -> AgentState:
    logger.info("Executing Profile Agent node")
    resume_text = state.get("resume_text", "")
    user_inputs = state.get("user_profile", {})

    settings = get_settings()

    if not settings.google_api_key or "your_gemini_api_key" in settings.google_api_key:
        logger.warning("Google API key missing, returning fallback canonical profile")
        fallback_profile = {
            "name": user_inputs.get("name", "Candidate"),
            "experience_level": "Senior Level",
            "education": {"degree": "B.S. Computer Science", "institution": "University", "year": 2021},
            "skills": ["Python", "FastAPI", "LangGraph", "Docker", "PostgreSQL", "React"],
            "projects": [{"title": "CareerOps Platform", "description": "Agentic AI Job Search System", "technologies": ["Python", "LangGraph"]}],
            "experience": [{"role": "Software Engineer", "company": "Tech Enterprise", "duration": "3 yrs", "highlights": ["Built AI agents"]}],
            "certifications": ["Python Professional Certificate"],
            "preferred_roles": ["Senior Software Engineer", "AI Engineer"],
            "locations": ["Remote"],
            "salary_expectation": {"currency": "USD", "min_base": 130000, "target_base": 150000}
        }
        return {**state, "canonical_profile": fallback_profile, "current_agent": "profile_agent", "error": None}

    try:
        llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.google_api_key,
            temperature=0.1
        )
        response = await llm.ainvoke([
            SystemMessage(content=PROFILE_EXTRACTION_SYSTEM),
            HumanMessage(content=f"Resume Text:\n{resume_text}\n\nAdditional Preferences:\n{json.dumps(user_inputs)}")
        ])

        res_text = response.content.strip()
        if res_text.startswith("```"):
            lines = [l for l in res_text.split("\n") if not l.strip().startswith("```")]
            res_text = "\n".join(lines)

        parsed_profile = json.loads(res_text)
        return {**state, "canonical_profile": parsed_profile, "current_agent": "profile_agent", "error": None}
    except Exception as e:
        logger.error("Failed to parse canonical profile", error=str(e))
        return {**state, "canonical_profile": {}, "current_agent": "profile_agent", "error": str(e)}
