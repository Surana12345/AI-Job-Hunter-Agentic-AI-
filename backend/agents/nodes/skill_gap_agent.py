"""
CareerOps - Skill-Gap & Career Intelligence Agent Node

Analyzes historical application outcome patterns to identify missing/weak skills
and updates job search strategy.
"""

from __future__ import annotations

import json
from typing import Any
from backend.agents.state import AgentState
from backend.utils.logger import get_logger

logger = get_logger("agents.skill_gap_agent")


async def skill_gap_agent_node(state: AgentState) -> AgentState:
    logger.info("Executing Skill-Gap & Career Intelligence Agent node")
    profile = state.get("canonical_profile", {})
    history = state.get("application_history", [])

    cand_skills = set([s.lower() for s in profile.get("skills", [])])
    missing_skill_counts: dict[str, int] = {}

    for app in history:
        missing_kw = app.get("missing_keywords", [])
        for kw in missing_kw:
            kw_clean = kw.lower()
            if kw_clean not in cand_skills:
                missing_skill_counts[kw_clean] = missing_skill_counts.get(kw_clean, 0) + 1

    sorted_gaps = sorted(missing_skill_counts.items(), key=lambda x: x[1], reverse=True)
    top_gaps = [item[0] for item in sorted_gaps[:5]]

    recommendations = []
    if top_gaps:
        recommendations.append(f"Consider acquiring certifications or adding projects for top missing skills: {', '.join(top_gaps)}.")
    else:
        recommendations.append("Your skills closely align with your target role postings.")

    career_intel = {
        "top_missing_skills": top_gaps,
        "frequency": dict(sorted_gaps[:5]),
        "recommendations": recommendations,
        "strategy_adjustment": "Refine job search to highlight strong technical competencies and target high-match titles."
    }

    return {
        **state,
        "career_intelligence": career_intel,
        "current_agent": "skill_gap_agent",
        "error": None,
    }
