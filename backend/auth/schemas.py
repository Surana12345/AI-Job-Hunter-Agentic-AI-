"""
AI Job Hunter - Authentication Pydantic Schemas

Request/response models for the authentication API endpoints.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# --- Request Schemas ---


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (8-128 characters)",
    )
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User's full name",
    )


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


# --- Response Schemas ---


class UserResponse(BaseModel):
    """Schema for user data in API responses."""

    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User's email address")
    full_name: str = Field(..., description="User's full name")
    is_active: bool = Field(..., description="Whether the account is active")
    created_at: datetime = Field(..., description="Account creation timestamp")

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Schema for JWT token response after login."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(..., description="Authenticated user data")


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str = Field(..., description="Response message")
    success: bool = Field(default=True, description="Whether the operation succeeded")
