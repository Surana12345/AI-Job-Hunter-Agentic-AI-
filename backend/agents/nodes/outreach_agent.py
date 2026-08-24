"""
CareerOps - Outreach Agent Node

Generates personalized recruiter/hiring manager cold outreach emails based on
verified candidate profile and job details.
"""

from __future__ import annotations

import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.state import AgentState
from backend.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger("agents.outreach_agent")

OUTREACH_SYSTEM = """You are a Professional Career Outreach Specialist.
Generate a high-converting, personalized cold email for a hiring manager or tech recruiter.

Return ONLY a valid JSON object matching:
{
    "recipient_role": "Technical Recruiter / Hiring Manager",
    "subject": "Senior AI Engineer Opportunity - Candidate Full Name",
    "email_body": "Hi [Hiring Manager Name],\n\nI noticed your opening for Senior AI Engineer at Acme Corp...",
    "call_to_action": "15-minute introductory call next week",
    "status": "DRAFT"
}
"""


async def outreach_agent_node(state: AgentState) -> AgentState:
    logger.info("Executing Outreach Agent node")
    profile = state.get("canonical_profile", {})
    job_title = state.get("job_title", "Software Engineer")
    job_company = state.get("job_company", "Target Company")

    settings = get_settings()

    if not settings.google_api_key or "your_gemini_api_key" in settings.google_api_key:
        fallback_email = {
            "recipient_role": "Talent Acquisition Manager",
            "subject": f"Inquiry regarding {job_title} role at {job_company}",
            "email_body": (
                f"Hi Hiring Team,\n\n"
                f"I came across the {job_title} position at {job_company} and wanted to reach out directly. "
                f"With my experience in Python backend microservices and agentic AI architectures, "
                f"I believe I can bring immediate value to your engineering organization.\n\n"
                f"I would welcome the opportunity to discuss how my background aligns with your team's current initiatives.\n\n"
                f"Best regards,\nCandidate"
            ),
            "call_to_action": "Brief 15-min call",
            "status": "DRAFT"
        }
        return {**state, "outreach_email": fallback_email, "current_agent": "outreach_agent", "error": None}

    try:
        llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.google_api_key,
            temperature=0.3
        )
        response = await llm.ainvoke([
            SystemMessage(content=OUTREACH_SYSTEM),
            HumanMessage(content=f"Candidate Profile: {json.dumps(profile)}\nTarget Role: {job_title}\nCompany: {job_company}")
        ])

        res_text = response.content.strip()
        if res_text.startswith("```"):
            lines = [l for l in res_text.split("\n") if not l.strip().startswith("```")]
            res_text = "\n".join(lines)

        parsed_email = json.loads(res_text)
        return {**state, "outreach_email": parsed_email, "current_agent": "outreach_agent", "error": None}
    except Exception as e:
        logger.error("Failed to generate outreach email", error=str(e))
        return {**state, "outreach_email": {}, "current_agent": "outreach_agent", "error": str(e)}
