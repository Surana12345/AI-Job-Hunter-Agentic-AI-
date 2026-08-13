"""
AI Job Hunter - Custom Exception Classes

Defines application-specific exceptions and FastAPI exception handlers
for consistent error responses across all endpoints.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception with HTTP status code and detail message."""

    def __init__(
        self,
        detail: str = "An unexpected error occurred",
        status_code: int = 500,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.detail = detail
        self.status_code = status_code
        self.headers = headers
        super().__init__(self.detail)


class NotFoundException(AppException):
    """Resource not found (404)."""

    def __init__(self, resource: str = "Resource", resource_id: Any = None) -> None:
        detail = f"{resource} not found"
        if resource_id is not None:
            detail = f"{resource} with id '{resource_id}' not found"
        super().__init__(detail=detail, status_code=404)


class UnauthorizedException(AppException):
    """Authentication required or failed (401)."""

    def __init__(self, detail: str = "Could not validate credentials") -> None:
        super().__init__(
            detail=detail,
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(AppException):
    """Access denied (403)."""

    def __init__(self, detail: str = "Access denied") -> None:
        super().__init__(detail=detail, status_code=403)


class BadRequestException(AppException):
    """Invalid request data (400)."""

    def __init__(self, detail: str = "Bad request") -> None:
        super().__init__(detail=detail, status_code=400)


class ConflictException(AppException):
    """Resource conflict, e.g. duplicate entry (409)."""

    def __init__(self, detail: str = "Resource already exists") -> None:
        super().__init__(detail=detail, status_code=409)


class RateLimitException(AppException):
    """Rate limit exceeded (429)."""

    def __init__(self, detail: str = "Rate limit exceeded. Please try again later.") -> None:
        super().__init__(detail=detail, status_code=429)


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI application.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "detail": exc.detail,
                "status_code": exc.status_code,
            },
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        # Log the full traceback for unexpected errors
        from backend.utils.logger import get_logger

        logger = get_logger("exception_handler")
        logger.error(
            "Unhandled exception",
            exc_type=type(exc).__name__,
            exc_detail=str(exc),
            path=str(request.url),
            method=request.method,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "detail": "An internal server error occurred",
                "status_code": 500,
            },
        )
