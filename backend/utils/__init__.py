"""
AI Job Hunter - Utilities Package
"""

from backend.utils.logger import get_logger, setup_logging
from backend.utils.exceptions import (
    AppException,
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
    RateLimitException,
    UnauthorizedException,
)
from backend.utils.helpers import (
    calculate_match_percentage,
    extract_file_extension,
    format_datetime,
    generate_id,
    sanitize_filename,
    truncate_text,
    utc_now,
)

__all__ = [
    # Logging
    "get_logger",
    "setup_logging",
    # Exceptions
    "AppException",
    "BadRequestException",
    "ConflictException",
    "ForbiddenException",
    "NotFoundException",
    "RateLimitException",
    "UnauthorizedException",
    # Helpers
    "calculate_match_percentage",
    "extract_file_extension",
    "format_datetime",
    "generate_id",
    "sanitize_filename",
    "truncate_text",
    "utc_now",
]
