# 🎯 CareerOps — Agentic AI Job Search & Application Automation Platform

An autonomous multi-agent career-operations platform built strictly according to the **CareerOps Product Blueprint & Architecture**.

Discovers relevant jobs, calculates weighted hybrid match scores, personalizes applications, maps form fields, sends personalized recruiter outreach, tracks application outcomes, and continuously learns from application results.

---

## 🌟 Master Architecture Overview

```
 USER PROFILE MEMORY
       │
       ▼
 RESUME / SKILL ANALYSIS (Profile Agent)
       │
       ▼
 JOB DISCOVERY (Connector Adapters: Remotive, Adzuna, Career Feeds)
       │
       ▼
 JOB NORMALIZATION & DEDUPLICATION
       │
       ▼
 HYBRID MATCHING & SCORING (Skills 30%, Exp 20%, Role 15%, Loc 10%, Sal 10%, Edu 10%, Fresh 5%)
       │
       ▼
 DECISION AGENT ROUTING (90-100 Full Auto | 80-89 Assisted | 70-79 Review | <70 Skip)
       │
  ┌────┴───────────────────────────┐
  ▼                                ▼
 APPLICATION AGENT              OUTREACH AGENT
 (Form Mapping, Policy Check)   (Recruiter Cold Emails)
  │                                │
  └────────────────┬───────────────┘
                   ▼
 APPLICATION TRACKER (DISCOVERED -> MATCHED -> READY -> APPLIED -> SHORTLISTED -> INTERVIEW -> OFFER)
                   │
                   ▼
 SKILL-GAP & CAREER INTELLIGENCE ANALYTICS (Outcome Feedback Loop)
```

---

## 🛠️ Multi-Agent System Modules

1. **Profile Agent (`profile_agent.py`)**:
   - Resume document parsing & structured extraction into a canonical candidate profile JSON schema.
   - Separates verified user facts from AI generations.

2. **Job Discovery Agent (`job_discovery.py`)**:
   - Connector/adapter architecture normalizing title, company, location, salary, description, and deduplicating jobs.

3. **Job Matching & Scoring Agent (`job_matching.py`)**:
   - Calculates weighted score: Skills (30%), Experience (20%), Role (15%), Location (10%), Salary (10%), Education (10%), Freshness (5%).
   - Action routing: `>=90 FULL_AUTO`, `80-89 ASSISTED`, `70-79 REVIEW`, `<70 SKIP`.

4. **Application Agent (`application_agent.py`)**:
   - Form field mapping from canonical profile & tailored response generation.
   - Enforces human-in-the-loop automation policies (`FULL_AUTO`, `ASSISTED`, `MANUAL`).

5. **Outreach Agent (`outreach_agent.py`)**:
   - Generates personalized recruiter cold emails & tracks recipient interaction status.

6. **Skill-Gap & Career Intelligence Agent (`skill_gap_agent.py`)**:
   - Feedback loop analyzing application outcome patterns to identify repeatedly missing skills and update search strategy.

---

## 💻 Quick Start & Running

```powershell
# Launch Unified CareerOps Web Server:
.\start_app.ps1
```

- **Web Application Portal**: `http://127.0.0.1:8000/`
- **3D Landing Page**: `http://127.0.0.1:8000/landing`
- **FastAPI OpenAPI Swagger Docs**: `http://127.0.0.1:8000/docs`
