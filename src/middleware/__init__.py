"""
Rate limiting middleware for FastAPI.

Uses slowapi to implement rate limiting per IP address.
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

from ..config import settings

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_calls}/{settings.rate_limit_period}second"],
)


def get_rate_limiter() -> Limiter:
    """Get the rate limiter instance."""
    return limiter


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Custom handler for rate limit exceeded errors."""
    response = Response(
        content={
            "error": "Rate limit exceeded",
            "detail": f"Too many requests. Limit: {exc.retry_after} seconds remaining.",
            "retry_after": exc.retry_after,
        },
        status_code=HTTP_429_TOO_MANY_REQUESTS,
        headers={"Retry-After": str(exc.retry_after)},
    )
    return response

