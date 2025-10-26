"""
Base API client with common functionality for all API clients.

This module provides a base class with retry logic, error handling,
and logging capabilities.
"""

from typing import Any, Dict, Optional
import httpx
from loguru import logger

from ..config import settings


class BaseAPIClient:
    """Base class for all API clients with common functionality."""

    def __init__(self, base_url: str, timeout: int = None) -> None:
        """
        Initialize the base API client.

        Args:
            base_url: The base URL for the API
            timeout: Request timeout in seconds (defaults to settings value)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout or settings.api_timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """
        Get or create an async HTTP client.

        Returns:
            An async HTTP client instance
        """
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                follow_redirects=True,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client connection."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request with error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            headers: Request headers

        Returns:
            Response data as dictionary

        Raises:
            httpx.HTTPError: If the request fails
        """
        client = await self._get_client()
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            logger.info(f"Making {method} request to {url}")
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers,
            )
            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            logger.error(f"Response content: {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
            raise

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make a GET request.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            headers: Request headers

        Returns:
            Response data as dictionary
        """
        return await self._make_request("GET", endpoint, params=params, headers=headers)

    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make a POST request.

        Args:
            endpoint: API endpoint path
            data: Request body data
            headers: Request headers

        Returns:
            Response data as dictionary
        """
        return await self._make_request("POST", endpoint, data=data, headers=headers)

    async def __aenter__(self):
        """Async context manager entry."""
        await self._get_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

