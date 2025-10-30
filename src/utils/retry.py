"""
Retry utilities with exponential backoff.

Provides retry logic for external API calls and other operations.
"""

import asyncio
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from loguru import logger

T = TypeVar("T")


async def retry_with_backoff(
    func: Callable[..., T],
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,),
    *args: Any,
    **kwargs: Any,
) -> T:
    """
    Retry a function with exponential backoff.

    Args:
        func: Async function to retry
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        exceptions: Tuple of exceptions to catch and retry
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func

    Returns:
        Result from successful function call

    Raises:
        Last exception if all attempts fail
    """
    last_exception = None

    for attempt in range(1, max_attempts + 1):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except exceptions as e:
            last_exception = e

            if attempt == max_attempts:
                logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                raise

            # Calculate delay with exponential backoff
            delay = min(initial_delay * (exponential_base ** (attempt - 1)), max_delay)

            logger.warning(
                f"Function {func.__name__} failed on attempt {attempt}/{max_attempts}: {e}. "
                f"Retrying in {delay:.2f}s..."
            )

            await asyncio.sleep(delay)

    # Should never reach here, but type checker needs it
    raise last_exception or Exception("Retry failed")


def retry_on_failure(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """
    Decorator for retrying functions with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        exceptions: Tuple of exceptions to catch and retry

    Returns:
        Decorated function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            return await retry_with_backoff(
                func,
                max_attempts=max_attempts,
                initial_delay=initial_delay,
                max_delay=max_delay,
                exponential_base=exponential_base,
                exceptions=exceptions,
                *args,
                **kwargs,
            )

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            # For sync functions, we need to handle differently
            # This is a simplified version
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        raise
                    import time

                    delay = min(initial_delay * (exponential_base ** (attempt - 1)), max_delay)
                    time.sleep(delay)

            raise last_exception or Exception("Retry failed")

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
