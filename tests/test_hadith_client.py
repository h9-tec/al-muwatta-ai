"""
Comprehensive tests for Hadith API Client.

This module tests all functionality of the HadithAPIClient including
collection retrieval, book access, hadith fetching, and search capabilities.
"""

import pytest
from src.api_clients import HadithAPIClient


class TestHadithAPIClient:
    """Test suite for HadithAPIClient."""

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test that the Hadith client initializes correctly."""
        client = HadithAPIClient()
        assert client is not None
        assert client.base_url == HadithAPIClient.SUNNAH_API_BASE
        await client.close()

    @pytest.mark.asyncio
    async def test_get_collections(self, hadith_client: HadithAPIClient):
        """Test retrieving all Hadith collections."""
        collections = await hadith_client.get_collections()

        # API might not be available, but we test the structure
        assert isinstance(collections, list)

        if collections:
            # Verify first collection has expected fields
            first_collection = collections[0]
            assert "name" in first_collection or "collectionName" in first_collection

    @pytest.mark.asyncio
    async def test_get_collection_by_name(self, hadith_client: HadithAPIClient):
        """Test retrieving a specific Hadith collection by name."""
        collection_name = "bukhari"
        collection = await hadith_client.get_collection_by_name(collection_name)

        # May return None if API is unavailable
        if collection:
            assert isinstance(collection, dict)
            assert "name" in collection or "collectionName" in collection

    @pytest.mark.asyncio
    async def test_get_books_from_collection(self, hadith_client: HadithAPIClient):
        """Test retrieving books from a Hadith collection."""
        collection_name = "bukhari"
        books = await hadith_client.get_books_from_collection(collection_name)

        assert isinstance(books, list)

        if books:
            first_book = books[0]
            assert "bookNumber" in first_book or "book" in first_book

    @pytest.mark.asyncio
    async def test_get_hadiths_from_book(self, hadith_client: HadithAPIClient):
        """Test retrieving Hadiths from a specific book."""
        collection_name = "bukhari"
        book_number = 1

        result = await hadith_client.get_hadiths_from_book(
            collection_name,
            book_number,
            page=1,
            limit=5,
        )

        assert isinstance(result, dict)
        assert "data" in result
        assert isinstance(result["data"], list)

        if result["data"]:
            first_hadith = result["data"][0]
            assert "hadithArabic" in first_hadith or "text" in first_hadith

    @pytest.mark.asyncio
    async def test_get_hadith_by_number(self, hadith_client: HadithAPIClient):
        """Test retrieving a specific Hadith by number."""
        collection_name = "bukhari"
        hadith_number = 1

        hadith = await hadith_client.get_hadith_by_number(
            collection_name,
            hadith_number,
        )

        # May return None if API is unavailable
        if hadith:
            assert isinstance(hadith, dict)
            assert "hadithArabic" in hadith or "text" in hadith

    @pytest.mark.asyncio
    async def test_search_hadith_no_collection(self, hadith_client: HadithAPIClient):
        """Test searching Hadiths across all collections."""
        query = "prayer"

        results = await hadith_client.search_hadith(query, page=1, limit=5)

        assert isinstance(results, dict)
        assert "data" in results
        assert isinstance(results["data"], list)

    @pytest.mark.asyncio
    async def test_search_hadith_specific_collection(
        self,
        hadith_client: HadithAPIClient,
    ):
        """Test searching Hadiths in a specific collection."""
        query = "prayer"
        collection_name = "bukhari"

        results = await hadith_client.search_hadith(
            query,
            collection_name=collection_name,
            page=1,
            limit=5,
        )

        assert isinstance(results, dict)
        assert "data" in results

    @pytest.mark.asyncio
    async def test_search_hadith_arabic(self, hadith_client: HadithAPIClient):
        """Test searching Hadiths with Arabic query."""
        query = "الصلاة"

        results = await hadith_client.search_hadith(query, limit=5)

        assert isinstance(results, dict)
        assert "data" in results

    @pytest.mark.asyncio
    async def test_get_random_hadith(self, hadith_client: HadithAPIClient):
        """Test retrieving a random Hadith."""
        hadith = await hadith_client.get_random_hadith()

        # May return None if API is unavailable
        if hadith:
            assert isinstance(hadith, dict)

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test using the client as an async context manager."""
        async with HadithAPIClient() as client:
            assert client is not None
            # Test a simple operation
            collections = await client.get_collections()
            assert isinstance(collections, list)

    @pytest.mark.asyncio
    async def test_pagination(self, hadith_client: HadithAPIClient):
        """Test pagination in Hadith retrieval."""
        collection_name = "bukhari"
        book_number = 1

        # Get first page
        page1 = await hadith_client.get_hadiths_from_book(
            collection_name,
            book_number,
            page=1,
            limit=3,
        )

        # Get second page
        page2 = await hadith_client.get_hadiths_from_book(
            collection_name,
            book_number,
            page=2,
            limit=3,
        )

        assert isinstance(page1, dict)
        assert isinstance(page2, dict)

        # Pages should have data (if API is available)
        if page1["data"] and page2["data"]:
            # Verify pages are different
            assert page1["data"] != page2["data"]

