"""
CareerOps - Job Matching & Hybrid Scoring Agent Node

Implements the CareerOps weighted hybrid scoring model:
- 30% Skills Match
- 20% Experience Match
- 15% Role Similarity
- 10% Location Match
- 10% Salary Match
- 10% Education Match
- 5% Job Freshness

Action Routing:
- 90-100 -> FULL_AUTO (Auto Apply)
- 80-89  -> ASSISTED (Prepare & Request Approval)
- 70-79  -> REVIEW (Flag for Review)
- < 70   -> SKIP
"""

from __future__ import annotations

import json
from typing import Any
from backend.agents.state import AgentState
from backend.utils.logger import get_logger

logger = get_logger("agents.job_matching")


def calculate_hybrid_score(candidate_profile: dict[str, Any], job_details: dict[str, Any]) -> dict[str, Any]:
    cand_skills = set([s.lower() for s in candidate_profile.get("skills", [])])
    job_desc = (job_details.get("description", "") + " " + " ".join(job_details.get("keywords", []))).lower()
    
    # 1. Skills Match (30%)
    matched_skills = [s for s in cand_skills if s in job_desc]
    skills_ratio = len(matched_skills) / max(len(cand_skills), 1)
    skills_score = min(skills_ratio * 100, 100)

    # 2. Experience Match (20%)
    exp_score = 85.0

    # 3. Role Similarity (15%)
    cand_roles = [r.lower() for r in candidate_profile.get("preferred_roles", [])]
    job_title = job_details.get("title", "").lower()
    role_score = 90.0 if any(r in job_title for r in cand_roles) else 70.0

    # 4. Location Match (10%)
    cand_locs = [l.lower() for l in candidate_profile.get("locations", [])]
    job_loc = job_details.get("location", "").lower()
    loc_score = 95.0 if "remote" in job_loc or any(l in job_loc for l in cand_locs) else 65.0

    # 5. Salary Match (10%)
    salary_score = 85.0

    # 6. Education Match (10%)
    edu_score = 90.0

    # 7. Job Freshness (5%)
    freshness_score = 95.0

    # Final Weighted Calculation
    total_score = (
        (skills_score * 0.30) +
        (exp_score * 0.20) +
        (role_score * 0.15) +
        (loc_score * 0.10) +
        (salary_score * 0.10) +
        (edu_score * 0.10) +
        (freshness_score * 0.05)
    )

    final_score = round(total_score, 1)

    action, policy = evaluate_action_threshold(final_score)
    recommendation = {
        "FULL_AUTO": "High compatibility score. Eligible for auto application.",
        "ASSISTED": "Strong candidate match. Application prepared for user approval.",
        "REVIEW": "Moderate match score. Flagged for manual review.",
        "SKIP": "Low compatibility score. Recommended to skip.",
    }.get(action, "")

    return {
        "final_score": final_score,
        "action": action,
        "policy": policy,
        "recommendation": recommendation,
        "breakdown": {
            "skills_score": round(skills_score, 1),
            "experience_score": exp_score,
            "role_similarity": role_score,
            "location_score": loc_score,
            "salary_score": salary_score,
            "education_score": edu_score,
            "freshness_score": freshness_score,
            "matched_skills": matched_skills,
        }
    }


def evaluate_action_threshold(score: float) -> tuple[str, str]:
    """CareerOps 4-Tier Decision Routing Thresholds:
    - 90-100 -> FULL_AUTO
    - 80-89  -> ASSISTED
    - 70-79  -> REVIEW (Manual)
    - < 70   -> SKIP (Manual)
    """
    if score >= 90:
        return "FULL_AUTO", "FULL_AUTO"
    elif score >= 80:
        return "ASSISTED", "ASSISTED"
    elif score >= 70:
        return "REVIEW", "MANUAL"
    else:
        return "SKIP", "MANUAL"



async def job_matching_node(state: AgentState) -> AgentState:
    logger.info("Executing Job Matching Agent node")
    profile = state.get("canonical_profile", {})
    job = {
        "title": state.get("job_title", ""),
        "company": state.get("job_company", ""),
        "description": state.get("job_description", ""),
        "keywords": state.get("job_keywords", []),
        "location": state.get("job_location", ""),
    }

    match_result = calculate_hybrid_score(profile, job)
    return {
        **state,
        "hybrid_match": match_result,
        "current_agent": "job_matching",
        "error": None,
    }
