"""
Security headers middleware.

Adds security headers to all responses for enhanced security.
"""

from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    
    Implements OWASP recommended security headers:
    - X-Content-Type-Options
    - X-Frame-Options
    - X-XSS-Protection
    - Strict-Transport-Security
    - Content-Security-Policy (optional)
    """
    
    def __init__(
        self,
        app: Callable,
        hsts_max_age: int = 31536000,  # 1 year
        content_security_policy: str | None = None,
    ):
        """
        Initialize security headers middleware.
        
        Args:
            app: ASGI application
            hsts_max_age: HSTS max-age in seconds
            content_security_policy: Optional CSP header value
        """
        super().__init__(app)
        self.hsts_max_age = hsts_max_age
        self.csp = content_security_policy
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and add security headers.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response with security headers
        """
        response = await call_next(request)
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # HSTS (only for HTTPS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                f"max-age={self.hsts_max_age}; includeSubDomains"
            )
        
        # Content Security Policy (if provided)
        if self.csp:
            response.headers["Content-Security-Policy"] = self.csp
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

