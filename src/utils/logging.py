"""
Structured logging utilities.

Provides structured logging with request context and correlation IDs.
"""

import sys
from typing import Any

from loguru import logger

# Remove default handler
logger.remove()


# Configure structured logging
def setup_logging(
    log_file: str = "logs/app.jsonl",
    log_level: str = "INFO",
    serialize: bool = True,
    rotation: str = "100 MB",
    retention: str = "30 days",
) -> None:
    """
    Configure structured logging.

    Args:
        log_file: Path to log file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        serialize: Whether to serialize logs as JSON
        rotation: Log rotation size
        retention: Log retention period
    """
    # Console handler with color
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )

    # File handler with JSON serialization
    if serialize:
        logger.add(
            log_file,
            format="{time} | {level} | {message}",
            level=log_level,
            rotation=rotation,
            retention=retention,
            serialize=True,  # JSON format
            enqueue=True,  # Async logging
        )
    else:
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=log_level,
            rotation=rotation,
            retention=retention,
            enqueue=True,
        )


def log_with_context(
    level: str, message: str, request_id: str | None = None, **context: Any
) -> None:
    """
    Log with structured context.

    Args:
        level: Log level (debug, info, warning, error)
        message: Log message
        request_id: Request correlation ID
        **context: Additional context fields
    """
    # Build context string for loguru
    context_parts = []
    if request_id:
        context_parts.append(f"request_id={request_id}")

    for key, value in context.items():
        context_parts.append(f"{key}={value}")

    context_str = " | ".join(context_parts) if context_parts else ""
    full_message = f"{message} | {context_str}" if context_str else message

    getattr(logger, level.lower())(full_message)


def get_request_id(request: Any | None = None) -> str | None:
    """
    Get request ID from request state.

    Args:
        request: FastAPI request object

    Returns:
        Request ID or None
    """
    if request and hasattr(request.state, "request_id"):
        return request.state.request_id
    return None
