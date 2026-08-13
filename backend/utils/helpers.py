"""
AI Job Hunter - General Helper Utilities

Shared utility functions used across multiple modules.
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from pathlib import Path


def generate_id() -> str:
    """Generate a unique ID string using UUID4.

    Returns:
        A 32-character hex string without hyphens.
    """
    return uuid.uuid4().hex


def utc_now() -> datetime:
    """Get the current UTC datetime (timezone-aware).

    Returns:
        Current datetime in UTC.
    """
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime | None) -> str | None:
    """Format a datetime to ISO 8601 string.

    Args:
        dt: Datetime to format, or None.

    Returns:
        ISO formatted string or None.
    """
    if dt is None:
        return None
    return dt.isoformat()


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename by removing unsafe characters.

    Args:
        filename: Original filename.

    Returns:
        Sanitized filename safe for filesystem use.
    """
    # Remove path separators and null bytes
    filename = filename.replace("/", "_").replace("\\", "_").replace("\0", "")
    # Remove any non-alphanumeric characters except dots, hyphens, underscores
    filename = re.sub(r"[^\w.\-]", "_", filename)
    # Limit length
    name = Path(filename).stem[:100]
    ext = Path(filename).suffix[:10]
    return f"{name}{ext}"


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """Truncate text to a maximum length with a suffix.

    Args:
        text: Text to truncate.
        max_length: Maximum character length.
        suffix: String to append if truncated.

    Returns:
        Truncated text string.
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def extract_file_extension(filename: str) -> str:
    """Extract the lowercase file extension from a filename.

    Args:
        filename: The filename to extract from.

    Returns:
        Lowercase extension including dot (e.g., '.pdf'), or empty string.
    """
    return Path(filename).suffix.lower()


def calculate_match_percentage(matched: int, total: int) -> float:
    """Calculate a percentage with safe division.

    Args:
        matched: Number of matched items.
        total: Total number of items.

    Returns:
        Percentage as float (0.0 to 100.0).
    """
    if total == 0:
        return 0.0
    return round((matched / total) * 100, 1)
