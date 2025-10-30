"""
Custom exceptions for Nur Al-Ilm API.

Provides a hierarchy of exceptions for better error handling and categorization.
"""

from typing import Optional, Dict, Any


class IslamicAPIError(Exception):
    """Base exception for all Islamic API errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(IslamicAPIError):
    """Validation error for invalid input."""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        super().__init__(message, status_code=400, error_code="VALIDATION_ERROR", **kwargs)
        self.field = field
        if self.field:
            self.details["field"] = self.field


class AuthenticationError(IslamicAPIError):
    """Authentication/authorization error."""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, status_code=401, error_code="AUTH_ERROR", **kwargs)


class NotFoundError(IslamicAPIError):
    """Resource not found error."""
    
    def __init__(self, message: str = "Resource not found", resource: Optional[str] = None, **kwargs):
        super().__init__(message, status_code=404, error_code="NOT_FOUND", **kwargs)
        self.resource = resource
        if self.resource:
            self.details["resource"] = self.resource


class RateLimitError(IslamicAPIError):
    """Rate limit exceeded error."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, status_code=429, error_code="RATE_LIMIT", **kwargs)
        self.retry_after = retry_after
        if self.retry_after:
            self.details["retry_after"] = self.retry_after


class ExternalAPIError(IslamicAPIError):
    """External API error."""
    
    def __init__(
        self,
        message: str,
        service: str,
        status_code: int = 502,
        original_error: Optional[Exception] = None,
        **kwargs
    ):
        super().__init__(message, status_code=status_code, error_code="EXTERNAL_API_ERROR", **kwargs)
        self.service = service
        self.original_error = original_error
        self.details["service"] = service
        if original_error:
            self.details["original_error"] = str(original_error)


class HadithAPIError(ExternalAPIError):
    """Hadith API specific errors."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None, **kwargs):
        super().__init__(message, service="hadith", original_error=original_error, **kwargs)


class QuranAPIError(ExternalAPIError):
    """Quran API specific errors."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None, **kwargs):
        super().__init__(message, service="quran", original_error=original_error, **kwargs)


class LLMServiceError(IslamicAPIError):
    """LLM service errors."""
    
    def __init__(
        self,
        message: str,
        provider: str = "unknown",
        original_error: Optional[Exception] = None,
        **kwargs
    ):
        super().__init__(message, status_code=503, error_code="LLM_ERROR", **kwargs)
        self.provider = provider
        self.original_error = original_error
        self.details["provider"] = provider
        if original_error:
            self.details["original_error"] = str(original_error)


class CacheError(IslamicAPIError):
    """Cache operation errors."""
    
    def __init__(self, message: str, operation: str = "unknown", **kwargs):
        super().__init__(message, status_code=500, error_code="CACHE_ERROR", **kwargs)
        self.operation = operation
        self.details["operation"] = operation

