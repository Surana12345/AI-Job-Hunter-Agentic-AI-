"""
AI Job Hunter - Inbound Email Classifier & Lifecycle Sync
Classifies recruiter emails via lightweight LLM and automatically updates application lifecycle status:
- Application Acknowledged -> APPLIED
- Interview Invitation -> INTERVIEWING
- Rejection Notice -> REJECTED
- Offer Letter -> OFFER
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from backend.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger("tracker.email_classifier")

CLASSIFIER_SYSTEM_PROMPT = """You are an automated inbound email classifier for job applications.
Analyze the incoming recruiter email and classify it into exactly ONE of these four categories:
1. APPLIED (Receipt/acknowledgement of application, e.g. "We received your application", "Thank you for applying")
2. INTERVIEWING (Interview invitation, screen call request, technical assessment link)
3. REJECTED (Rejection letter, e.g. "We decided to pursue other candidates", "Unfortunately")
4. OFFER (Offer letter, compensation proposal, congratulatory offer)

Return ONLY a valid JSON object matching:
{
    "category": "INTERVIEWING",
    "confidence": 0.95,
    "company": "Company Name",
    "job_title": "Role Name",
    "key_details": "Recruiter invited candidate for a 30-min technical screen next Tuesday.",
    "action_required": true
}
"""


class InboundEmailClassifier:
    """Classifies incoming emails and synchronizes application lifecycle states."""

    @staticmethod
    async def classify_email(email_text: str, subject: str = "", sender: str = "") -> Dict[str, Any]:
        """Classify incoming email text into a lifecycle status."""
        logger.info("Classifying inbound email", subject=subject, sender=sender)
        settings = get_settings()

        combined_text = f"From: {sender}\nSubject: {subject}\n\n{email_text}"

        if not settings.google_api_key or "your_gemini_api_key" in settings.google_api_key:
            # Rule-based heuristics fallback
            text_lower = combined_text.lower()
            if any(w in text_lower for w in ["offer", "congratulations", "pleased to offer"]):
                cat = "OFFER"
            elif any(w in text_lower for w in ["interview", "screen", "chat with the team", "schedule time", "assessment"]):
                cat = "INTERVIEWING"
            elif any(w in text_lower for w in ["unfortunately", "pursue other candidates", "not moving forward"]):
                cat = "REJECTED"
            else:
                cat = "APPLIED"

            return {
                "category": cat,
                "confidence": 0.88,
                "company": "Recruiting Team",
                "job_title": "Applied Position",
                "key_details": f"Classified via heuristic engine based on subject: {subject}",
                "action_required": cat in ["INTERVIEWING", "OFFER"],
            }

        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=settings.google_api_key,
                temperature=0.1,
            )
            res = await llm.ainvoke([
                SystemMessage(content=CLASSIFIER_SYSTEM_PROMPT),
                HumanMessage(content=combined_text),
            ])
            content = res.content.strip()
            if content.startswith("```"):
                lines = [l for l in content.split("\n") if not l.strip().startswith("```")]
                content = "\n".join(lines)
            data = json.loads(content)
            logger.info("Email classified successfully", category=data.get("category"), confidence=data.get("confidence"))
            return data
        except Exception as e:
            logger.error("LLM email classification error, using fallback", error=str(e))
            return {
                "category": "APPLIED",
                "confidence": 0.70,
                "company": "Company",
                "key_details": "Application acknowledged.",
                "action_required": False,
            }
