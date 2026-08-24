"""
AI Job Hunter - Streamlit Frontend API Client

HTTP Client wrapper for interacting with the FastAPI backend API.
"""

from __future__ import annotations

from typing import Any, Optional

import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"


class APIClient:
    """Client for FastAPI Backend endpoints."""

    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.headers = {}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def register(self, email: str, password: str, full_name: str) -> dict:
        url = f"{BASE_URL}/auth/register"
        resp = requests.post(url, json={"email": email, "password": password, "full_name": full_name})
        resp.raise_for_status()
        return resp.json()

    def login(self, email: str, password: str) -> dict:
        url = f"{BASE_URL}/auth/login"
        resp = requests.post(url, json={"email": email, "password": password})
        resp.raise_for_status()
        return resp.json()

    def get_me(self) -> dict:
        url = f"{BASE_URL}/auth/me"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    # --- Resume Endpoints ---
    def upload_resume(self, file_bytes: bytes, filename: str, content_type: str, is_primary: bool = False) -> dict:
        url = f"{BASE_URL}/resume/upload?is_primary={str(is_primary).lower()}"
        files = {"file": (filename, file_bytes, content_type)}
        resp = requests.post(url, headers=self.headers, files=files)
        resp.raise_for_status()
        return resp.json()

    def list_resumes(self) -> list[dict]:
        url = f"{BASE_URL}/resume/list"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def parse_resume(self, resume_id: str) -> dict:
        url = f"{BASE_URL}/resume/{resume_id}/parse"
        resp = requests.post(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def analyze_ats(self, resume_id: str, job_description: str, job_title: str = "", job_company: str = "") -> dict:
        url = f"{BASE_URL}/resume/analyze-ats"
        payload = {
            "resume_id": resume_id,
            "job_description": job_description,
            "job_title": job_title,
            "job_company": job_company,
        }
        resp = requests.post(url, headers=self.headers, json=payload)
        resp.raise_for_status()
        return resp.json()

    # --- Job Endpoints ---
    def search_jobs(self, query: str, location: str = "", job_type: str = "", max_results: int = 15) -> list[dict]:
        url = f"{BASE_URL}/jobs/search"
        payload = {
            "query": query,
            "location": location,
            "job_type": job_type,
            "max_results": max_results,
        }
        resp = requests.post(url, headers=self.headers, json=payload)
        resp.raise_for_status()
        return resp.json()

    def list_jobs(self, saved_only: bool = False) -> list[dict]:
        url = f"{BASE_URL}/jobs/list?saved_only={str(saved_only).lower()}"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def toggle_job_saved(self, job_id: str) -> dict:
        url = f"{BASE_URL}/jobs/{job_id}/toggle-saved"
        resp = requests.put(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def research_company(self, company_name: str, job_title: str = "") -> dict:
        url = f"{BASE_URL}/jobs/research-company"
        payload = {"company_name": company_name, "job_title": job_title}
        resp = requests.post(url, headers=self.headers, json=payload)
        resp.raise_for_status()
        return resp.json()

    # --- Assets Endpoints ---
    def generate_cover_letter(self, resume_id: str, job_description: str, job_title: str, company_name: str) -> dict:
        url = f"{BASE_URL}/assets/cover-letter"
        payload = {
            "resume_id": resume_id,
            "job_description": job_description,
            "job_title": job_title,
            "company_name": company_name,
        }
        resp = requests.post(url, headers=self.headers, json=payload)
        resp.raise_for_status()
        return resp.json()

    def generate_recruiter_message(self, resume_id: str, job_title: str, company_name: str, platform: str = "LinkedIn") -> dict:
        url = f"{BASE_URL}/assets/recruiter-message"
        payload = {
            "resume_id": resume_id,
            "job_title": job_title,
            "company_name": company_name,
            "platform": platform,
        }
        resp = requests.post(url, headers=self.headers, json=payload)
        resp.raise_for_status()
        return resp.json()

    def generate_interview_prep(self, resume_id: str, job_description: str, company_name: str, role_title: str) -> dict:
        url = f"{BASE_URL}/assets/interview-prep"
        payload = {
            "resume_id": resume_id,
            "job_description": job_description,
            "company_name": company_name,
            "role_title": role_title,
        }
        resp = requests.post(url, headers=self.headers, json=payload)
        resp.raise_for_status()
        return resp.json()

    def export_application_pdf(
        self,
        job_title: str,
        company_name: str,
        cover_letter: str = "",
        tailored_resume: str = "",
        recruiter_message: str = "",
        interview_prep: Optional[dict] = None,
    ) -> bytes:
        url = f"{BASE_URL}/assets/export-pdf"
        payload = {
            "job_title": job_title,
            "company_name": company_name,
            "cover_letter": cover_letter,
            "tailored_resume": tailored_resume,
            "recruiter_message": recruiter_message,
            "interview_prep": interview_prep,
        }
        resp = requests.post(url, headers=self.headers, json=payload)
        resp.raise_for_status()
        return resp.content

    def evaluate_mock_interview(self, job_title: str, company_name: str, question: str, candidate_answer: str) -> dict:
        url = f"{BASE_URL}/assets/mock-interview/evaluate"
        payload = {
            "job_title": job_title,
            "company_name": company_name,
            "question": question,
            "candidate_answer": candidate_answer,
        }
        resp = requests.post(url, headers=self.headers, json=payload)
        resp.raise_for_status()
        return resp.json()



    # --- Tracker Endpoints ---
    def create_application_track(self, job_title: str, company_name: str, location: str = "", status: str = "saved") -> dict:
        url = f"{BASE_URL}/tracker"
        payload = {
            "job_title": job_title,
            "company_name": company_name,
            "location": location,
            "status": status,
        }
        resp = requests.post(url, headers=self.headers, json=payload)
        resp.raise_for_status()
        return resp.json()

    def list_application_tracks(self, status: str = "") -> list[dict]:
        url = f"{BASE_URL}/tracker/list?status={status}"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def get_tracker_analytics(self) -> dict:
        url = f"{BASE_URL}/tracker/analytics"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def update_application_track(self, track_id: str, status: Optional[str] = None, notes: Optional[str] = None) -> dict:
        url = f"{BASE_URL}/tracker/{track_id}"
        payload = {}
        if status:
            payload["status"] = status
        if notes:
            payload["notes"] = notes
        resp = requests.patch(url, headers=self.headers, json=payload)
        resp.raise_for_status()
        return resp.json()
