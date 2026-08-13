"""
AI Job Hunter - Authentication Service Layer

Business logic for user registration, login, and retrieval.
Decoupled from HTTP/FastAPI concerns.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.models import User
from backend.auth.schemas import UserCreate, UserLogin
from backend.auth.utils import create_access_token, hash_password, verify_password
from backend.utils.exceptions import (
    ConflictException,
    NotFoundException,
    UnauthorizedException,
)
from backend.utils.logger import get_logger

logger = get_logger("auth.service")


class AuthService:
    """Service class for authentication operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def register_user(self, data: UserCreate) -> tuple[User, str]:
        """Register a new user account.

        Args:
            data: User registration data.

        Returns:
            Tuple of (created User, JWT access token).

        Raises:
            ConflictException: If email is already registered.
        """
        # Check if email already exists
        existing = await self._get_user_by_email(data.email)
        if existing:
            raise ConflictException(f"User with email '{data.email}' already exists")

        # Create user
        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
        )
        self.db.add(user)
        await self.db.flush()

        # Generate token
        token = create_access_token(user_id=user.id, email=user.email)

        logger.info("User registered", user_id=user.id, email=user.email)
        return user, token

    async def login_user(self, data: UserLogin) -> tuple[User, str]:
        """Authenticate a user and return a JWT token.

        Args:
            data: User login credentials.

        Returns:
            Tuple of (authenticated User, JWT access token).

        Raises:
            UnauthorizedException: If credentials are invalid.
        """
        user = await self._get_user_by_email(data.email)

        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")

        # Generate token
        token = create_access_token(user_id=user.id, email=user.email)

        logger.info("User logged in", user_id=user.id, email=user.email)
        return user, token

    async def get_user_by_id(self, user_id: str) -> User:
        """Retrieve a user by their ID.

        Args:
            user_id: The user's database ID.

        Returns:
            The User instance.

        Raises:
            NotFoundException: If user doesn't exist.
        """
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundException("User", user_id)

        return user

    async def _get_user_by_email(self, email: str) -> User | None:
        """Look up a user by email address.

        Args:
            email: Email to search for.

        Returns:
            User instance or None if not found.
        """
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
