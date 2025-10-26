"""
Quran API Client for fetching Quranic verses, translations, and recitations.

This client interfaces with:
- api.alquran.cloud (free, comprehensive Quran API)
- quran.com API (alternative)
"""

from typing import Any, Dict, List, Optional

from loguru import logger

from .base_client import BaseAPIClient


class QuranAPIClient(BaseAPIClient):
    """Client for accessing Quranic content from various sources."""

    # API Documentation: https://alquran.cloud/api
    ALQURAN_API_BASE = "https://api.alquran.cloud/v1"

    def __init__(self) -> None:
        """Initialize the Quran API client."""
        super().__init__(base_url=self.ALQURAN_API_BASE)

    async def get_full_quran(
        self,
        edition: str = "quran-uthmani",
    ) -> Optional[Dict[str, Any]]:
        """
        Get the complete Quran in specified edition.

        Args:
            edition: Quran edition identifier
                - 'quran-uthmani': Arabic Uthmani script
                - 'en.sahih': Sahih International English translation
                - 'ar.alafasy': Arabic with Alafasy recitation

        Returns:
            Complete Quran data or None if request fails

        Example:
            >>> client = QuranAPIClient()
            >>> quran = await client.get_full_quran('quran-uthmani')
            >>> print(quran['numberOfSurahs'])
            114
        """
        try:
            response = await self.get(f"/quran/{edition}")
            return response.get("data")
        except Exception as e:
            logger.error(f"Failed to get full Quran (edition={edition}): {e}")
            return None

    async def get_surah(
        self,
        surah_number: int,
        edition: str = "quran-uthmani",
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific Surah (chapter) by number.

        Args:
            surah_number: Surah number (1-114)
            edition: Quran edition identifier

        Returns:
            Surah data with all ayahs or None if not found

        Example:
            >>> client = QuranAPIClient()
            >>> al_fatiha = await client.get_surah(1, edition='en.sahih')
            >>> print(al_fatiha['englishName'])
            'Al-Faatiha'
            >>> for ayah in al_fatiha['ayahs']:
            ...     print(ayah['text'])
        """
        try:
            if not 1 <= surah_number <= 114:
                raise ValueError("Surah number must be between 1 and 114")

            response = await self.get(f"/surah/{surah_number}/{edition}")
            return response.get("data")
        except ValueError as e:
            logger.error(f"Invalid surah number: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to get Surah {surah_number}: {e}")
            return None

    async def get_ayah(
        self,
        ayah_reference: str,
        edition: str = "quran-uthmani",
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific Ayah (verse) by reference.

        Args:
            ayah_reference: Ayah reference in format 'surah:ayah' (e.g., '2:255')
            edition: Quran edition identifier

        Returns:
            Ayah data or None if not found

        Example:
            >>> client = QuranAPIClient()
            >>> ayah_al_kursi = await client.get_ayah('2:255', edition='en.sahih')
            >>> print(ayah_al_kursi['text'])
        """
        try:
            response = await self.get(f"/ayah/{ayah_reference}/{edition}")
            return response.get("data")
        except Exception as e:
            logger.error(f"Failed to get Ayah {ayah_reference}: {e}")
            return None

    async def get_ayah_by_number(
        self,
        ayah_number: int,
        edition: str = "quran-uthmani",
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific Ayah by its absolute number in the Quran.

        Args:
            ayah_number: Ayah number (1-6236)
            edition: Quran edition identifier

        Returns:
            Ayah data or None if not found

        Example:
            >>> client = QuranAPIClient()
            >>> ayah = await client.get_ayah_by_number(1)
            >>> print(ayah['text'])
        """
        try:
            if not 1 <= ayah_number <= 6236:
                raise ValueError("Ayah number must be between 1 and 6236")

            response = await self.get(f"/ayah/{ayah_number}/{edition}")
            return response.get("data")
        except ValueError as e:
            logger.error(f"Invalid ayah number: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to get Ayah number {ayah_number}: {e}")
            return None

    async def get_juz(
        self,
        juz_number: int,
        edition: str = "quran-uthmani",
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific Juz (part) of the Quran.

        Args:
            juz_number: Juz number (1-30)
            edition: Quran edition identifier

        Returns:
            Juz data with all ayahs or None if not found

        Example:
            >>> client = QuranAPIClient()
            >>> juz = await client.get_juz(30)
            >>> print(juz['surahs'])
        """
        try:
            if not 1 <= juz_number <= 30:
                raise ValueError("Juz number must be between 1 and 30")

            response = await self.get(f"/juz/{juz_number}/{edition}")
            return response.get("data")
        except ValueError as e:
            logger.error(f"Invalid juz number: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to get Juz {juz_number}: {e}")
            return None

    async def get_page(
        self,
        page_number: int,
        edition: str = "quran-uthmani",
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific page of the Quran.

        Args:
            page_number: Page number (1-604)
            edition: Quran edition identifier

        Returns:
            Page data with all ayahs or None if not found

        Example:
            >>> client = QuranAPIClient()
            >>> page = await client.get_page(1)
            >>> for ayah in page['ayahs']:
            ...     print(ayah['text'])
        """
        try:
            if not 1 <= page_number <= 604:
                raise ValueError("Page number must be between 1 and 604")

            response = await self.get(f"/page/{page_number}/{edition}")
            return response.get("data")
        except ValueError as e:
            logger.error(f"Invalid page number: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to get page {page_number}: {e}")
            return None

    async def get_editions(
        self,
        format_type: Optional[str] = None,
        language: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all available Quran editions/translations.

        Args:
            format_type: Filter by format ('text', 'audio')
            language: Filter by language code ('en', 'ar', 'ur', etc.)

        Returns:
            List of available editions

        Example:
            >>> client = QuranAPIClient()
            >>> editions = await client.get_editions(language='en')
            >>> for edition in editions:
            ...     print(edition['identifier'], edition['englishName'])
        """
        try:
            endpoint = "/edition"
            params = {}

            if format_type:
                params["format"] = format_type
            if language:
                params["language"] = language

            response = await self.get(endpoint, params=params if params else None)
            return response.get("data", [])
        except Exception as e:
            logger.error(f"Failed to get editions: {e}")
            return []

    async def search_quran(
        self,
        query: str,
        surah: Optional[int] = None,
        edition: str = "quran-uthmani",
    ) -> Dict[str, Any]:
        """
        Search for verses in the Quran.

        Args:
            query: Search query (Arabic or transliteration)
            surah: Limit search to specific Surah (optional)
            edition: Quran edition to search in

        Returns:
            Search results with matching ayahs

        Example:
            >>> client = QuranAPIClient()
            >>> results = await client.search_quran('الله', surah=1)
            >>> for match in results['matches']:
            ...     print(match['text'])
        """
        try:
            params = {"q": query}
            if surah:
                params["surah"] = surah

            response = await self.get(f"/search/{query}/{edition}", params=params)
            return response.get("data", {"matches": [], "count": 0})
        except Exception as e:
            logger.error(f"Failed to search Quran with query '{query}': {e}")
            return {"matches": [], "count": 0}

    async def get_surah_with_multiple_editions(
        self,
        surah_number: int,
        editions: List[str],
    ) -> Optional[Dict[str, Any]]:
        """
        Get a Surah with multiple editions/translations at once.

        Args:
            surah_number: Surah number (1-114)
            editions: List of edition identifiers

        Returns:
            Surah data with multiple editions or None if request fails

        Example:
            >>> client = QuranAPIClient()
            >>> surah = await client.get_surah_with_multiple_editions(
            ...     1,
            ...     ['quran-uthmani', 'en.sahih', 'en.pickthall']
            ... )
            >>> for edition in surah:
            ...     print(edition['edition']['englishName'])
        """
        try:
            if not 1 <= surah_number <= 114:
                raise ValueError("Surah number must be between 1 and 114")

            editions_str = ",".join(editions)
            response = await self.get(f"/surah/{surah_number}/editions/{editions_str}")
            return response.get("data")
        except ValueError as e:
            logger.error(f"Invalid surah number: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to get Surah {surah_number} with multiple editions: {e}")
            return None

