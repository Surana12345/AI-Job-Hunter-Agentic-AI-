# 🎯 AI Job Hunter -- Agentic AI Career Assistant

An autonomous multi-agent platform powered by **LangGraph**, **Gemini 2.5 Flash**, **ChromaDB**, **FastAPI**, and **Streamlit**. 

**Important Constraint:** Designed strictly to empower candidates — it **never automatically submits applications or impersonates you on job platforms**. It prepares personalized, ATS-optimized application packages for your review.

---

## 🌟 Architecture & Vision

```
                      +----------------------------------+
                      |   Streamlit Multi-Page Frontend  |
                      +----------------------------------+
                                       |
                                       v
                      +----------------------------------+
                      |     FastAPI Async REST API       |
                      +----------------------------------+
                                       |
                                       v
                  +------------------------------------------+
                  |  LangGraph Multi-Agent Orchestrator     |
                  +------------------------------------------+
                    /          |           |            \
                   v           v           v             v
             Resume Agent   ATS Agent  Tailor Agent   Company Agent
                   \           |           |            /
                    +----------+-----------+-----------+
                                       |
                                       v
                     +-----------------------------------+
                     | ChromaDB Vectorstore + Embeddings |
                     +-----------------------------------+
```

### Key Highlights
- **🤖 Multi-Agent Orchestration**: State machine pipeline built on **LangGraph** routing tasks dynamically between specialized agents.
- **📄 Resume Intelligence**: Extracts text from PDF/DOCX files, parses structured JSON skills, and stores vector embeddings in **ChromaDB**.
- **🎯 ATS Match & Keyword Gap**: Calculates keyword overlap, match percentage, and missing skills vs job descriptions.
- **🔍 Multi-Source Job Discovery**: Searches technical roles across Remotive and Adzuna APIs with instant bookmarking.
- **✨ Career Assets Generator**: AI-generated tailored Cover Letters, LinkedIn/Email outreach messages, and Technical/Behavioral Interview Prep Guides.
- **📊 Application Pipeline Tracker**: Kanban/Table dashboard tracking application stages (`saved`, `applied`, `interview`, `offer`, `rejected`) and conversion analytics.

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|------------|
| **Agent Orchestration** | LangGraph, LangChain |
| **LLM Intelligence** | Google Gemini (`gemini-2.5-flash`) |
| **Vector DB & Embeddings** | ChromaDB, Sentence-Transformers (`all-MiniLM-L6-v2`) |
| **Backend Framework** | FastAPI, Uvicorn, Async SQLAlchemy, SQLite |
| **Document Parsing** | PyPDF2, python-docx |
| **Security & Auth** | JWT (JSON Web Tokens), Direct Bcrypt Password Hashing |
| **Frontend UI** | Streamlit (Multi-page App, Custom Dark Glassmorphic Theme) |

---

## 🚀 Quick Start & Installation

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/your-username/ai-job-hunter.git
cd "AI Job Hunter (Agentic AI)"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and set your Google Gemini API key:
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
JWT_SECRET_KEY=dev-secret-key-change-in-production
```

---

## 💻 Running the Application

### Option A: Local Development Launchers
Run both Backend and Frontend concurrently using the automated script:
```powershell
.\start_app.ps1
```
Or run separately:
```bash
# Terminal 1: Backend FastAPI
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Streamlit Dashboard
streamlit run frontend/app.py
```

### Option B: Docker Containerized Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build -d
```
- FastAPI Server: `http://localhost:8000`
- Streamlit Dashboard: `http://localhost:8501`

---

## 📡 API Endpoints Overview (34 Endpoints)

- **Authentication**: `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`
- **Resume Intelligence**: `POST /api/v1/resume/upload`, `POST /api/v1/resume/{id}/parse`, `POST /api/v1/resume/analyze-ats`, `GET /api/v1/resume/list`
- **Job Search & Research**: `POST /api/v1/jobs/search`, `GET /api/v1/jobs/list`, `POST /api/v1/jobs/research-company`
- **Career Assets**: `POST /api/v1/assets/cover-letter`, `POST /api/v1/assets/recruiter-message`, `POST /api/v1/assets/interview-prep`
- **Application Tracker**: `POST /api/v1/tracker`, `GET /api/v1/tracker/list`, `GET /api/v1/tracker/analytics`, `PATCH /api/v1/tracker/{id}`

---

## 📜 License
MIT License. Built for empowerment and ethical AI career assistance.
