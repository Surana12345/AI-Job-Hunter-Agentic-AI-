"""
AI Job Hunter - Authentication API Router

Endpoints for user registration, login, and profile retrieval.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.schemas import (
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from backend.auth.service import AuthService
from backend.dependencies import get_current_user, get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=201,
    summary="Register a new user account",
    description="Create a new user account with email, password, and full name. "
    "Returns a JWT access token on successful registration.",
)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Register a new user and return JWT token."""
    service = AuthService(db)
    user, token = await service.register_user(data)

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password",
    description="Authenticate with email and password. "
    "Returns a JWT access token on successful login.",
)
async def login(
    data: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate user and return JWT token."""
    service = AuthService(db)
    user, token = await service.login_user(data)

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Retrieve the profile of the currently authenticated user. "
    "Requires a valid JWT token in the Authorization header.",
)
async def get_me(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Get the current authenticated user's profile."""
    service = AuthService(db)
    user = await service.get_user_by_id(current_user["sub"])

    return UserResponse.model_validate(user)
