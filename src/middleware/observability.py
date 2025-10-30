"""
Comprehensive observability middleware for Al-Muwatta.

Implements structured logging, metrics, tracing, and health checks.
"""

import contextvars
import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

# Context variable for request ID
request_id_var = contextvars.ContextVar("request_id", default=None)


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive observability.

    Features:
    - Request ID generation and propagation
    - Structured logging with context
    - Request/response timing
    - Error tracking

    Example:
        >>> app.add_middleware(ObservabilityMiddleware)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with full observability.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response with observability headers
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)

        # Start timing
        start_time = time.time()

        # Extract request metadata
        method = request.method
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Structured logging - Request start
        logger.bind(
            request_id=request_id,
            method=method,
            path=path,
            client_host=client_host,
            user_agent=user_agent,
        ).info(f"Request started: {method} {path}")

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Structured logging - Request complete
            logger.bind(
                request_id=request_id,
                method=method,
                path=path,
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
            ).info(f"Request completed: {method} {path} - {response.status_code}")

            # Add observability headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration:.3f}s"

            return response

        except Exception as exc:
            # Calculate duration
            duration = time.time() - start_time

            # Structured logging - Request failed
            logger.bind(
                request_id=request_id,
                method=method,
                path=path,
                duration_ms=round(duration * 1000, 2),
                error=str(exc),
                error_type=type(exc).__name__,
            ).error(f"Request failed: {method} {path}")

            raise


def get_request_id() -> str:
    """
    Get current request ID from context.

    Returns:
        Request ID string or 'unknown' if not set
    """
    return request_id_var.get() or "unknown"
