"""
Comprehensive tests for Quran API Client.

This module tests all functionality of the QuranAPIClient including
Surah retrieval, Ayah access, Juz/page queries, and edition management.
"""

import pytest

from src.api_clients import QuranAPIClient


class TestQuranAPIClient:
    """Test suite for QuranAPIClient."""

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test that the Quran client initializes correctly."""
        client = QuranAPIClient()
        assert client is not None
        assert client.base_url == QuranAPIClient.ALQURAN_API_BASE
        await client.close()

    @pytest.mark.asyncio
    async def test_get_surah(self, quran_client: QuranAPIClient):
        """Test retrieving a specific Surah."""
        surah_number = 1  # Al-Fatiha

        surah = await quran_client.get_surah(surah_number)

        assert surah is not None
        assert isinstance(surah, dict)
        assert "number" in surah
        assert surah["number"] == 1
        assert "ayahs" in surah
        assert len(surah["ayahs"]) == 7  # Al-Fatiha has 7 verses

    @pytest.mark.asyncio
    async def test_get_surah_with_translation(self, quran_client: QuranAPIClient):
        """Test retrieving a Surah with English translation."""
        surah_number = 1
        edition = "en.sahih"

        surah = await quran_client.get_surah(surah_number, edition=edition)

        assert surah is not None
        assert isinstance(surah, dict)
        assert "ayahs" in surah

        if surah["ayahs"]:
            first_ayah = surah["ayahs"][0]
            assert "text" in first_ayah

    @pytest.mark.asyncio
    async def test_get_surah_invalid_number(self, quran_client: QuranAPIClient):
        """Test retrieving a Surah with invalid number."""
        surah_number = 115  # Invalid (max is 114)

        surah = await quran_client.get_surah(surah_number)

        assert surah is None

    @pytest.mark.asyncio
    async def test_get_ayah_by_reference(self, quran_client: QuranAPIClient):
        """Test retrieving Ayah Al-Kursi (2:255)."""
        ayah_reference = "2:255"

        ayah = await quran_client.get_ayah(ayah_reference)

        assert ayah is not None
        assert isinstance(ayah, dict)
        assert "text" in ayah
        assert ayah["numberInSurah"] == 255

    @pytest.mark.asyncio
    async def test_get_ayah_by_number(self, quran_client: QuranAPIClient):
        """Test retrieving an Ayah by its absolute number."""
        ayah_number = 1  # First Ayah in Quran

        ayah = await quran_client.get_ayah_by_number(ayah_number)

        assert ayah is not None
        assert isinstance(ayah, dict)
        assert "text" in ayah

    @pytest.mark.asyncio
    async def test_get_ayah_invalid_number(self, quran_client: QuranAPIClient):
        """Test retrieving an Ayah with invalid number."""
        ayah_number = 7000  # Invalid (max is 6236)

        ayah = await quran_client.get_ayah_by_number(ayah_number)

        assert ayah is None

    @pytest.mark.asyncio
    async def test_get_juz(self, quran_client: QuranAPIClient):
        """Test retrieving a specific Juz."""
        juz_number = 30  # Last Juz

        juz = await quran_client.get_juz(juz_number)

        assert juz is not None
        assert isinstance(juz, dict)
        assert "ayahs" in juz
        assert isinstance(juz["ayahs"], list)

    @pytest.mark.asyncio
    async def test_get_juz_invalid_number(self, quran_client: QuranAPIClient):
        """Test retrieving a Juz with invalid number."""
        juz_number = 31  # Invalid (max is 30)

        juz = await quran_client.get_juz(juz_number)

        assert juz is None

    @pytest.mark.asyncio
    async def test_get_page(self, quran_client: QuranAPIClient):
        """Test retrieving a specific page."""
        page_number = 1  # First page

        page = await quran_client.get_page(page_number)

        assert page is not None
        assert isinstance(page, dict)
        assert "ayahs" in page
        assert isinstance(page["ayahs"], list)

    @pytest.mark.asyncio
    async def test_get_page_invalid_number(self, quran_client: QuranAPIClient):
        """Test retrieving a page with invalid number."""
        page_number = 605  # Invalid (max is 604)

        page = await quran_client.get_page(page_number)

        assert page is None

    @pytest.mark.asyncio
    async def test_get_editions(self, quran_client: QuranAPIClient):
        """Test retrieving all available editions."""
        editions = await quran_client.get_editions()

        assert isinstance(editions, list)
        assert len(editions) > 0

        # Check structure of first edition
        first_edition = editions[0]
        assert "identifier" in first_edition
        assert "language" in first_edition
        assert "englishName" in first_edition

    @pytest.mark.asyncio
    async def test_get_editions_by_language(self, quran_client: QuranAPIClient):
        """Test filtering editions by language."""
        language = "en"

        editions = await quran_client.get_editions(language=language)

        assert isinstance(editions, list)

        if editions:
            # All editions should be in English
            for edition in editions:
                assert edition["language"] == language

    @pytest.mark.asyncio
    async def test_get_editions_by_format(self, quran_client: QuranAPIClient):
        """Test filtering editions by format."""
        format_type = "text"

        editions = await quran_client.get_editions(format_type=format_type)

        assert isinstance(editions, list)

        if editions:
            for edition in editions:
                assert edition["format"] == format_type

    @pytest.mark.asyncio
    async def test_search_quran(self, quran_client: QuranAPIClient):
        """Test searching the Quran."""
        query = "الله"  # Allah in Arabic

        results = await quran_client.search_quran(query)

        assert isinstance(results, dict)
        assert "matches" in results or "count" in results

    @pytest.mark.asyncio
    async def test_search_quran_in_surah(self, quran_client: QuranAPIClient):
        """Test searching within a specific Surah."""
        query = "الله"
        surah = 1  # Al-Fatiha

        results = await quran_client.search_quran(query, surah=surah)

        assert isinstance(results, dict)

    @pytest.mark.asyncio
    async def test_get_surah_with_multiple_editions(
        self,
        quran_client: QuranAPIClient,
    ):
        """Test retrieving a Surah with multiple editions."""
        surah_number = 1
        editions = ["quran-uthmani", "en.sahih"]

        result = await quran_client.get_surah_with_multiple_editions(
            surah_number,
            editions,
        )

        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 2

        # Each edition should have the Surah data
        for surah_data in result:
            assert "ayahs" in surah_data
            assert len(surah_data["ayahs"]) == 7

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test using the client as an async context manager."""
        async with QuranAPIClient() as client:
            assert client is not None
            surah = await client.get_surah(1)
            assert surah is not None
            assert isinstance(surah, dict)

    @pytest.mark.asyncio
    async def test_full_quran_retrieval(self, quran_client: QuranAPIClient):
        """Test retrieving the complete Quran."""
        quran = await quran_client.get_full_quran()

        if quran:  # API might have size limits
            assert isinstance(quran, dict)
            assert "surahs" in quran
            assert len(quran["surahs"]) == 114
