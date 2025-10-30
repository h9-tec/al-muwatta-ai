"""
Request correlation middleware.

Adds correlation IDs to requests for distributed tracing and log correlation.
"""

import uuid
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class CorrelationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add correlation IDs to requests.

    Adds X-Request-ID header to all requests and responses for tracing.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and add correlation ID.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response with correlation ID header
        """
        # Get or generate request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Store in request state for access in handlers
        request.state.request_id = request_id

        # Process request
        response = await call_next(request)

        # Add correlation ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response
