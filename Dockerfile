# Multi-stage Dockerfile for AI Job Hunter

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Create required directories
RUN mkdir -p data/uploads data/generated data/chroma_db

# Expose ports: 8000 (FastAPI), 8501 (Streamlit)
EXPOSE 8000
EXPOSE 8501

# Default command launches FastAPI backend
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
