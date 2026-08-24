# 🎯 AI Job Hunter -- Agentic AI Career Assistant

An autonomous multi-agent platform powered by **LangGraph**, **Gemini 2.5 Flash**, **ChromaDB**, **FastAPI**, and **Streamlit**. 

**Important Constraint:** Designed strictly to empower candidates — it **never automatically submits applications or impersonates you on job platforms**. It prepares personalized, ATS-optimized application packages for your review.

---

## 🌟 Architecture & Vision

```
                      +----------------------------------+
                      |   Streamlit Multi-Page Frontend  |
                      |          (9 Interactive Pages)   |
                      +----------------------------------+
                                       |
                                       v
                      +----------------------------------+
                      |     FastAPI Async REST API       |
                      |      (38 Active Endpoints)       |
                      +----------------------------------+
                                       |
                                       v
                  +------------------------------------------+
                  |  LangGraph Multi-Agent Orchestrator     |
                  +------------------------------------------+
                    /          |           |            \
                   v           v           v             v
             Resume Agent   ATS Agent  Tailor Agent   Company Agent
             Cover Letter  Outreach    Mock Interview Negotiator
                   \           |           |            /
                    +----------+-----------+-----------+
                                       |
                                       v
                     +-----------------------------------+
                     | ChromaDB Vectorstore + Embeddings |
                     +-----------------------------------+
```

### Key Highlights
- **🤖 Multi-Agent Orchestration**: State machine pipeline built on **LangGraph** routing tasks dynamically between 10 specialized agent nodes.
- **📄 Resume Intelligence**: Extracts text from PDF/DOCX files, parses structured JSON skills, and stores vector embeddings in **ChromaDB**.
- **🎯 ATS Match & Keyword Gap**: Calculates keyword overlap, match percentage, and missing skills vs job descriptions.
- **🔍 Multi-Source Job Discovery**: Searches technical roles across Remotive and Adzuna APIs with instant bookmarking.
- **✨ Career Assets Generator**: AI-generated tailored Cover Letters, LinkedIn/Email outreach messages, and Technical/Behavioral Interview Prep Guides.
- **📊 Application Pipeline Tracker**: Kanban/Table dashboard tracking application stages (`saved`, `applied`, `interview`, `offer`, `rejected`) and conversion analytics.
- **📦 Application Package Exporter (PDF)**: Formats and exports compiled PDF application dossiers containing cover letters, resume overviews, outreach strategies, and interview guides.
- **🎙️ AI Mock Interview Simulator**: Real-time interactive mock interview evaluation with 1-10 scoring, STAR feedback, model answers, and follow-up questions.
- **💰 Salary Negotiation & Offer Evaluator**: Offer evaluation, market benchmarks (25th/50th/75th percentile), counter-offer email generator, and negotiation tactics.

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|------------|
| **Agent Orchestration** | LangGraph, LangChain |
| **LLM Intelligence** | Google Gemini (`gemini-2.5-flash`) |
| **Vector DB & Embeddings** | ChromaDB, Sentence-Transformers (`all-MiniLM-L6-v2`) |
| **Backend Framework** | FastAPI, Uvicorn, Async SQLAlchemy, SQLite |
| **Document & PDF Export** | PyPDF2, python-docx, ReportLab |
| **Security & Auth** | JWT (JSON Web Tokens), Direct Bcrypt Password Hashing |
| **Frontend UI** | Streamlit (Multi-page App - 9 Interactive Modules) |

---

## 🚀 Quick Start & Installation

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/Surana12345/AI-Job-Hunter-Agentic-AI-.git
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

### Option A: Local Development Launcher (Recommended)
Run both Backend and Frontend concurrently using the automated script:
```powershell
.\start_app.ps1
```
- Streamlit Dashboard: `http://localhost:8501`
- FastAPI Docs: `http://127.0.0.1:8000/docs`

### Option B: Docker Containerized Deployment
```bash
docker-compose up --build -d
```

---

## 📜 License
MIT License. Built for candidate empowerment and ethical AI career assistance.
