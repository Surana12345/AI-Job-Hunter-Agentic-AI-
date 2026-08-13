"""
AI Job Hunter - FastAPI Dependency Injection

Shared dependencies injected into route handlers via FastAPI's Depends().
Provides database sessions, authenticated user context, and LLM clients.
"""

from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.engine import get_async_session
from backend.utils.exceptions import UnauthorizedException

# Security scheme for Swagger UI
security = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency: yields an async database session.

    Automatically commits on success, rolls back on error,
    and closes the session when done.
    """
    async for session in get_async_session():
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Dependency: extracts and validates the current user from the JWT token.

    Args:
        credentials: Bearer token from the Authorization header.

    Returns:
        Decoded JWT payload containing user_id ('sub') and email.

    Raises:
        UnauthorizedException: If token is missing, invalid, or expired.
    """
    token = credentials.credentials

    from backend.auth.utils import decode_access_token

    payload = decode_access_token(token)
    if payload is None:
        raise UnauthorizedException("Invalid or expired token")

    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException("Invalid token payload")

    return payload


async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Dependency: validates that the current user is active.

    Performs a database lookup to ensure the user account
    hasn't been deactivated since the token was issued.

    Args:
        current_user: Decoded JWT payload.
        db: Database session.

    Returns:
        The validated JWT payload.

    Raises:
        UnauthorizedException: If the user account is inactive.
    """
    from backend.auth.models import User
    from sqlalchemy import select

    stmt = select(User).where(User.id == current_user["sub"])
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise UnauthorizedException("User account is inactive")

    return current_user
