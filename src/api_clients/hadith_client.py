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


class HadithAPIClient(BaseAPIClient):
    """Client for accessing Hadith collections from various sources."""

    # API Documentation: https://sunnah.api-docs.io/
    SUNNAH_API_BASE = "https://api.sunnah.com/v1"

    # Alternative free Hadith API
    HADITH_API_BASE = "https://random-hadith-generator.vercel.app"

    def __init__(self) -> None:
        """Initialize the Hadith API client."""
        super().__init__(base_url=self.SUNNAH_API_BASE)

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
            response = await self.get("/collections")
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
            response = await self.get(f"/collections/{collection_name}")
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
            response = await self.get(f"/collections/{collection_name}/books")
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
                f"/collections/{collection_name}/hadiths/{hadith_number}"
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

            response = await self.get(endpoint, params=params)
            return response
        except Exception as e:
            logger.error(f"Failed to search Hadiths with query '{query}': {e}")
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

            return response.get("data")
        except Exception as e:
            logger.error(f"Failed to get random Hadith: {e}")
            return None

