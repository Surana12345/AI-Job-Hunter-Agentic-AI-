"""
AI Job Hunter - Application Configuration

Central settings management using Pydantic BaseSettings.
All configuration is loaded from environment variables or .env file.
"""

from __future__ import annotations

from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root directory (parent of backend/)
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "AI Job Hunter"
    app_version: str = "1.0.0"
    debug: bool = True
    log_level: str = "INFO"

    # --- Authentication ---
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440  # 24 hours

    # --- Database ---
    database_url: str = f"sqlite+aiosqlite:///{BASE_DIR / 'data' / 'job_hunter.db'}"

    # --- Google Gemini ---
    google_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # --- ChromaDB ---
    chroma_persist_dir: str = str(BASE_DIR / "data" / "chroma_db")
    chroma_collection_resumes: str = "resumes"
    chroma_collection_jobs: str = "jobs"

    # --- Embedding Model ---
    embedding_model: str = "all-MiniLM-L6-v2"

    # --- File Storage ---
    upload_dir: str = str(BASE_DIR / "data" / "uploads")
    generated_dir: str = str(BASE_DIR / "data" / "generated")

    # --- Job Sources ---
    adzuna_app_id: str = ""
    adzuna_api_key: str = ""

    # --- Server ---
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # --- Frontend ---
    backend_url: str = "http://localhost:8000"
    streamlit_port: int = 8501

    def ensure_directories(self) -> None:
        """Create required data directories if they don't exist."""
        for dir_path in [self.upload_dir, self.generated_dir, self.chroma_persist_dir]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)

        # Ensure the database directory exists
        db_path = self.database_url.split("///")[-1]
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings singleton."""
    settings = Settings()
    settings.ensure_directories()
    return settings
