"""
Hadith API Client for fetching authentic Hadith collections.

This client interfaces with multiple Hadith APIs including:
- sunnah.com API
- hadithapi.com
- hadith.p.rapidapi.com (free tier)
"""

from typing import Any, Dict, List, Optional

from loguru import logger

from .base_client import BaseAPIClient
from ..config import settings


class HadithAPIClient(BaseAPIClient):
    """Client for accessing Hadith collections from various sources."""

    # API Documentation: https://sunnah.api-docs.io/
    SUNNAH_API_BASE = "https://api.sunnah.com/v1"

    # Alternative free Hadith API
    HADITH_API_BASE = "https://random-hadith-generator.vercel.app"
    ALT_HADITH_SOURCE = "https://api.hadith.gading.dev"

    def __init__(self) -> None:
        """Initialize the Hadith API client."""
        super().__init__(base_url=self.SUNNAH_API_BASE)
        self.sunnah_headers = {}
        if settings.sunnah_api_key:
            self.sunnah_headers["X-API-Key"] = settings.sunnah_api_key

    async def get_collections(self) -> List[Dict[str, Any]]:
        """
        Get all available Hadith collections.

        Returns:
            List of available Hadith collections with metadata

        Example:
            >>> client = HadithAPIClient()
            >>> collections = await client.get_collections()
            >>> print(collections[0]['name'])
            'Sahih Bukhari'
        """
        try:
            response = await self.get("/collections", headers=self.sunnah_headers or None)
            logger.info(f"Retrieved {len(response.get('data', []))} Hadith collections")
            return response.get("data", [])
        except Exception as e:
            logger.error(f"Failed to get Hadith collections: {e}")
            return []

    async def get_collection_by_name(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific Hadith collection by name.

        Args:
            collection_name: Name of the collection (e.g., 'bukhari', 'muslim')

        Returns:
            Collection metadata or None if not found

        Example:
            >>> client = HadithAPIClient()
            >>> bukhari = await client.get_collection_by_name('bukhari')
            >>> print(bukhari['totalHadith'])
        """
        try:
            response = await self.get(
                f"/collections/{collection_name}",
                headers=self.sunnah_headers or None,
            )
            return response.get("data")
        except Exception as e:
            logger.error(f"Failed to get collection '{collection_name}': {e}")
            return None

    async def get_books_from_collection(self, collection_name: str) -> List[Dict[str, Any]]:
        """
        Get all books from a specific Hadith collection.

        Args:
            collection_name: Name of the collection (e.g., 'bukhari')

        Returns:
            List of books in the collection

        Example:
            >>> client = HadithAPIClient()
            >>> books = await client.get_books_from_collection('bukhari')
            >>> print(books[0]['bookNumber'])
        """
        try:
            response = await self.get(
                f"/collections/{collection_name}/books",
                headers=self.sunnah_headers or None,
            )
            return response.get("data", [])
        except Exception as e:
            logger.error(f"Failed to get books from '{collection_name}': {e}")
            return []

    async def get_hadiths_from_book(
        self,
        collection_name: str,
        book_number: int,
        page: int = 1,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Get Hadiths from a specific book in a collection.

        Args:
            collection_name: Name of the collection (e.g., 'bukhari')
            book_number: Book number within the collection
            page: Page number for pagination
            limit: Number of Hadiths per page

        Returns:
            Dictionary containing Hadiths and pagination info

        Example:
            >>> client = HadithAPIClient()
            >>> hadiths = await client.get_hadiths_from_book('bukhari', 1, page=1, limit=10)
            >>> for hadith in hadiths['data']:
            ...     print(hadith['hadithNumber'], hadith['hadithArabic'])
        """
        try:
            params = {"page": page, "limit": limit}
            response = await self.get(
                f"/collections/{collection_name}/books/{book_number}/hadiths",
                params=params,
                headers=self.sunnah_headers or None,
            )
            return response
        except Exception as e:
            logger.error(
                f"Failed to get Hadiths from '{collection_name}' book {book_number}: {e}"
            )
            return {"data": [], "total": 0, "limit": limit, "page": page}

    async def get_hadith_by_number(
        self,
        collection_name: str,
        hadith_number: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific Hadith by its number.

        Args:
            collection_name: Name of the collection (e.g., 'bukhari')
            hadith_number: Hadith number within the collection

        Returns:
            Hadith data or None if not found

        Example:
            >>> client = HadithAPIClient()
            >>> hadith = await client.get_hadith_by_number('bukhari', 1)
            >>> print(hadith['hadithArabic'])
            >>> print(hadith['hadithEnglish'])
        """
        try:
            response = await self.get(
                f"/collections/{collection_name}/hadiths/{hadith_number}",
                headers=self.sunnah_headers or None,
            )
            return response.get("data")
        except Exception as e:
            logger.error(
                f"Failed to get Hadith #{hadith_number} from '{collection_name}': {e}"
            )
            return None

    async def search_hadith(
        self,
        query: str,
        collection_name: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Search for Hadiths matching a query.

        Args:
            query: Search query (Arabic or English)
            collection_name: Specific collection to search (optional)
            page: Page number for pagination
            limit: Number of results per page

        Returns:
            Dictionary containing search results and pagination info

        Example:
            >>> client = HadithAPIClient()
            >>> results = await client.search_hadith("prayer", collection_name="bukhari")
            >>> for hadith in results['data']:
            ...     print(hadith['hadithEnglish'])
        """
        try:
            params = {"q": query, "page": page, "limit": limit}
            endpoint = "/hadiths/search"
            if collection_name:
                endpoint = f"/collections/{collection_name}/hadiths/search"

            response = await self.get(endpoint, params=params, headers=self.sunnah_headers or None)
            if response.get("data"):
                return response
        except Exception as e:
            logger.error(f"Failed to search Hadiths with query '{query}': {e}")

        # Fallback to gading.dev API
        try:
            fallback_params = {"query": query, "limit": limit}
            fallback_client = BaseAPIClient(base_url="https://api.hadith.gading.dev")
            fallback_response = await fallback_client.get(
                "/search",
                params=fallback_params,
            )
            await fallback_client.close()
            data = fallback_response.get("data", [])
            return {
                "data": data,
                "total": len(data),
                "page": page,
                "limit": limit,
            }
        except Exception as fallback_error:
            logger.error(f"Fallback hadith search failed: {fallback_error}")
            return {"data": [], "total": 0, "limit": limit, "page": page}

    async def get_random_hadith(self) -> Optional[Dict[str, Any]]:
        """
        Get a random Hadith from various collections.

        Uses the Random Hadith Generator API as fallback.

        Returns:
            Random Hadith data or None if request fails

        Example:
            >>> client = HadithAPIClient()
            >>> hadith = await client.get_random_hadith()
            >>> print(hadith['hadithEnglish'])
        """
        try:
            # Use alternative free API for random Hadith
            client = BaseAPIClient(base_url=self.HADITH_API_BASE)
            response = await client.get("/hadiths")
            await client.close()

            random_hadith = response.get("data")
            if random_hadith:
                return random_hadith

            # Fallback to Gading.dev Hadith API
            try:
                fallback_client = BaseAPIClient(base_url=self.ALT_HADITH_SOURCE)
                fallback = await fallback_client.get("/books/bukhari", params={"range": "1-1"})
                await fallback_client.close()
                data = fallback.get("data", {}).get("hadiths")
                if data:
                    return data[0]
            except Exception as fallback_error:
                logger.error(f"Fallback random Hadith source failed: {fallback_error}")

            return None
        except Exception as e:
            logger.error(f"Failed to get random Hadith: {e}")
            return None

