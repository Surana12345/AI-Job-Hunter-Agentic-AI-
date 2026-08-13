"""
AI Job Hunter - FastAPI Application Entry Point

Creates and configures the FastAPI application with:
- CORS middleware
- Lifespan events (startup/shutdown)
- Router registration
- Exception handlers
- Health check endpoint
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.database.migrations import create_all_tables
from backend.utils.exceptions import register_exception_handlers
from backend.utils.logger import get_logger, setup_logging

settings = get_settings()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager — runs on startup and shutdown.

    Startup:
        - Configure structured logging
        - Create data directories
        - Initialize database tables

    Shutdown:
        - Clean up resources
    """
    # --- Startup ---
    setup_logging()
    logger.info(
        "Starting application",
        app_name=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )

    # Ensure data directories exist
    settings.ensure_directories()

    # Create database tables
    await create_all_tables()

    logger.info("Application started successfully")

    yield

    # --- Shutdown ---
    logger.info("Shutting down application")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance.

    Returns:
        Configured FastAPI application.
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Agentic AI Career Assistant — Multi-agent platform that discovers jobs, "
            "analyzes ATS compatibility, tailors resumes, researches companies, "
            "and prepares personalized career materials."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # --- Middleware ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Tighten in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Exception Handlers ---
    register_exception_handlers(app)

    # --- Routers ---
    from backend.auth.router import router as auth_router
    from backend.resume.router import router as resume_router
    from backend.jobs.router import router as jobs_router
    from backend.assets.router import router as assets_router
    from backend.tracker.router import router as tracker_router

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(resume_router, prefix="/api/v1")
    app.include_router(jobs_router, prefix="/api/v1")
    app.include_router(assets_router, prefix="/api/v1")
    app.include_router(tracker_router, prefix="/api/v1")

    # --- Health Check ---
    @app.get(
        "/health",
        tags=["System"],
        summary="Health check",
        description="Returns application health status and version.",
    )
    async def health_check() -> dict:
        return {
            "status": "healthy",
            "app": settings.app_name,
            "version": settings.app_version,
        }

    @app.get(
        "/",
        tags=["System"],
        summary="Root endpoint",
        include_in_schema=False,
    )
    async def root() -> dict:
        return {
            "message": f"Welcome to {settings.app_name} API",
            "version": settings.app_version,
            "docs": "/docs",
        }

    return app


# Application instance for uvicorn
app = create_app()
