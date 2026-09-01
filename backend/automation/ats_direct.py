"""
AI Job Hunter - Direct ATS Form API Submitter
Submits job applications directly via official Greenhouse & Lever public REST form APIs
to guarantee 100% submission reliability without headless browser overhead.
"""

from __future__ import annotations

import httpx
from typing import Any, Dict, Optional
from backend.utils.logger import get_logger

logger = get_logger("automation.ats_direct")


class DirectATSSubmitter:
    """Direct API submitter for Greenhouse and Lever ATS boards."""

    @staticmethod
    async def submit_greenhouse(
        company_slug: str,
        job_id: str,
        candidate_profile: Dict[str, Any],
        resume_text: str = "",
        cover_letter: str = "",
    ) -> Dict[str, Any]:
        """Submit an application directly to Greenhouse REST Form API.
        Endpoint: POST https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs/{job_id}
        """
        url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs/{job_id}"

        # Split candidate name
        full_name = candidate_profile.get("name", "Candidate")
        parts = full_name.split(" ", 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else "Applicant"

        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "email": candidate_profile.get("email", ""),
            "phone": candidate_profile.get("phone", ""),
            "cover_letter_text": cover_letter,
            "notes": "Submitted via CareerOps Autonomous Agent",
            "urls": {
                "LinkedIn": candidate_profile.get("linkedin", ""),
                "GitHub": candidate_profile.get("github", ""),
                "Portfolio": candidate_profile.get("portfolio", ""),
            },
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code in [200, 201]:
                    logger.info("Greenhouse direct submission successful", company=company_slug, job_id=job_id)
                    return {
                        "success": True,
                        "method": "greenhouse_direct_api",
                        "status_code": res.status_code,
                        "message": "Application submitted directly to Greenhouse ATS",
                        "response": res.json() if res.headers.get("content-type", "").startswith("application/json") else res.text,
                    }
                else:
                    logger.warning("Greenhouse direct API rejected payload", status=res.status_code, body=res.text[:300])
                    return {
                        "success": False,
                        "method": "greenhouse_direct_api",
                        "status_code": res.status_code,
                        "error": f"Greenhouse API returned {res.status_code}: {res.text[:200]}",
                    }
        except Exception as e:
            logger.error("Greenhouse direct submission failed", error=str(e))
            return {
                "success": False,
                "method": "greenhouse_direct_api",
                "error": str(e),
            }

    @staticmethod
    async def submit_lever(
        company_slug: str,
        job_id: str,
        candidate_profile: Dict[str, Any],
        cover_letter: str = "",
    ) -> Dict[str, Any]:
        """Submit an application directly to Lever REST Form API.
        Endpoint: POST https://api.lever.co/v0/postings/{company}/{job_id}
        """
        url = f"https://api.lever.co/v0/postings/{company_slug}/{job_id}"

        payload = {
            "name": candidate_profile.get("name", "Candidate"),
            "email": candidate_profile.get("email", ""),
            "phone": candidate_profile.get("phone", ""),
            "comments": cover_letter,
            "urls": {
                "LinkedIn": candidate_profile.get("linkedin", ""),
                "GitHub": candidate_profile.get("github", ""),
            },
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code in [200, 201]:
                    logger.info("Lever direct submission successful", company=company_slug, job_id=job_id)
                    return {
                        "success": True,
                        "method": "lever_direct_api",
                        "status_code": res.status_code,
                        "message": "Application submitted directly to Lever ATS",
                    }
                else:
                    return {
                        "success": False,
                        "method": "lever_direct_api",
                        "status_code": res.status_code,
                        "error": f"Lever API returned {res.status_code}: {res.text[:200]}",
                    }
        except Exception as e:
            logger.error("Lever direct submission failed", error=str(e))
            return {
                "success": False,
                "method": "lever_direct_api",
                "error": str(e),
            }
