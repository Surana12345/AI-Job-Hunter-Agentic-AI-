"""
AI Job Hunter - Resume Tools

Tools for resume text manipulation, section extraction, and formatting.
"""

from __future__ import annotations

import re
from typing import Any


def extract_resume_sections(resume_text: str) -> dict[str, str]:
    """Extract common sections from raw resume text.

    Uses heuristic pattern matching to identify standard resume sections
    like Experience, Education, Skills, etc.

    Args:
        resume_text: The raw resume text.

    Returns:
        Dict mapping section names to their content.
    """
    # Common resume section headers
    section_patterns = [
        r"(?i)(professional\s+summary|summary|objective|profile)",
        r"(?i)(work\s+experience|experience|employment\s+history|professional\s+experience)",
        r"(?i)(education|academic|qualifications)",
        r"(?i)(skills|technical\s+skills|core\s+competencies|competencies)",
        r"(?i)(projects|key\s+projects|personal\s+projects)",
        r"(?i)(certifications?|licenses?|credentials)",
        r"(?i)(awards?|honors?|achievements?)",
        r"(?i)(publications?|research)",
        r"(?i)(languages?)",
        r"(?i)(interests?|hobbies)",
    ]

    sections: dict[str, str] = {}
    lines = resume_text.split("\n")

    current_section = "header"
    current_content: list[str] = []

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            current_content.append("")
            continue

        # Check if this line is a section header
        is_header = False
        for pattern in section_patterns:
            if re.match(pattern, line_stripped):
                # Save previous section
                if current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = line_stripped.lower()
                current_content = []
                is_header = True
                break

        if not is_header:
            current_content.append(line)

    # Save last section
    if current_content:
        sections[current_section] = "\n".join(current_content).strip()

    return sections


def format_skills_list(skills: list[str]) -> str:
    """Format a skills list for display or comparison.

    Args:
        skills: List of skill strings.

    Returns:
        Formatted, deduplicated, sorted skills string.
    """
    # Normalize and deduplicate
    normalized = sorted(set(skill.strip().title() for skill in skills if skill.strip()))
    return ", ".join(normalized)


def calculate_keyword_overlap(
    resume_keywords: list[str],
    job_keywords: list[str],
) -> dict[str, Any]:
    """Calculate keyword overlap between resume and job description.

    Args:
        resume_keywords: Keywords extracted from the resume.
        job_keywords: Keywords extracted from the job description.

    Returns:
        Dict with matched, missing, match_percentage.
    """
    resume_set = {k.lower().strip() for k in resume_keywords}
    job_set = {k.lower().strip() for k in job_keywords}

    matched = resume_set & job_set
    missing = job_set - resume_set
    extra = resume_set - job_set

    total = len(job_set) if job_set else 1
    percentage = round((len(matched) / total) * 100, 1)

    return {
        "matched": sorted(matched),
        "missing": sorted(missing),
        "extra": sorted(extra),
        "match_percentage": percentage,
        "matched_count": len(matched),
        "total_required": len(job_set),
    }
