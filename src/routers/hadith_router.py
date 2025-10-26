"""
Hadith API Router.

This router provides endpoints for accessing and searching Hadith collections.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from ..api_clients import HadithAPIClient
from ..services import GeminiService
from ..models.schemas import HadithRequest, HadithResponse

router = APIRouter(prefix="/api/v1/hadith", tags=["Hadith"])


@router.get("/collections", summary="Get all Hadith collections")
async def get_hadith_collections() -> List[Dict[str, Any]]:
    """
    Retrieve all available Hadith collections.

    Returns:
        List of Hadith collections with metadata
    """
    async with HadithAPIClient() as client:
        collections = await client.get_collections()
        return collections


@router.get(
    "/collections/{collection_name}",
    summary="Get specific Hadith collection",
)
async def get_hadith_collection(collection_name: str) -> Dict[str, Any]:
    """
    Retrieve information about a specific Hadith collection.

    Args:
        collection_name: Name of the collection (e.g., 'bukhari')

    Returns:
        Collection metadata
    """
    async with HadithAPIClient() as client:
        collection = await client.get_collection_by_name(collection_name)

        if not collection:
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_name}' not found",
            )

        return collection


@router.get(
    "/collections/{collection_name}/books",
    summary="Get books from collection",
)
async def get_books_from_collection(
    collection_name: str,
) -> List[Dict[str, Any]]:
    """
    Retrieve all books from a specific Hadith collection.

    Args:
        collection_name: Name of the collection

    Returns:
        List of books in the collection
    """
    async with HadithAPIClient() as client:
        books = await client.get_books_from_collection(collection_name)
        return books


@router.get(
    "/collections/{collection_name}/books/{book_number}/hadiths",
    summary="Get Hadiths from a book",
)
async def get_hadiths_from_book(
    collection_name: str,
    book_number: int,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
) -> Dict[str, Any]:
    """
    Retrieve Hadiths from a specific book.

    Args:
        collection_name: Collection name
        book_number: Book number
        page: Page number for pagination
        limit: Number of Hadiths per page

    Returns:
        Paginated Hadiths data
    """
    async with HadithAPIClient() as client:
        hadiths = await client.get_hadiths_from_book(
            collection_name,
            book_number,
            page=page,
            limit=limit,
        )
        return hadiths


@router.get(
    "/collections/{collection_name}/hadiths/{hadith_number}",
    summary="Get specific Hadith",
)
async def get_hadith_by_number(
    collection_name: str,
    hadith_number: int,
    explain: bool = Query(False, description="Get AI explanation"),
    language: str = Query("english", description="Explanation language"),
) -> Dict[str, Any]:
    """
    Retrieve a specific Hadith by number with optional AI explanation.

    Args:
        collection_name: Collection name
        hadith_number: Hadith number
        explain: Whether to include AI explanation
        language: Language for explanation

    Returns:
        Hadith data with optional explanation
    """
    async with HadithAPIClient() as client:
        hadith = await client.get_hadith_by_number(collection_name, hadith_number)

        if not hadith:
            raise HTTPException(
                status_code=404,
                detail=f"Hadith #{hadith_number} not found in '{collection_name}'",
            )

        result = {
            "hadith": hadith,
            "source": "sunnah.com API",
        }

        if explain:
            gemini = GeminiService()
            hadith_text = hadith.get("hadithArabic") or hadith.get("text", "")
            explanation = await gemini.explain_hadith(hadith_text, language=language)

            result["explanation"] = explanation
            result["explanation_language"] = language

        return result


@router.get("/search", summary="Search Hadiths")
async def search_hadiths(
    query: str = Query(..., description="Search query"),
    collection_name: str = Query(None, description="Specific collection"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
) -> Dict[str, Any]:
    """
    Search for Hadiths across collections or in a specific collection.

    Args:
        query: Search query (Arabic or English)
        collection_name: Optional collection to search in
        page: Page number
        limit: Results per page

    Returns:
        Search results with pagination
    """
    async with HadithAPIClient() as client:
        results = await client.search_hadith(
            query,
            collection_name=collection_name,
            page=page,
            limit=limit,
        )
        return results


@router.get("/random", summary="Get random Hadith")
async def get_random_hadith(
    explain: bool = Query(False, description="Get AI explanation"),
    language: str = Query("english", description="Explanation language"),
) -> Dict[str, Any]:
    """
    Get a random Hadith with optional AI explanation.

    Args:
        explain: Whether to include AI explanation
        language: Language for explanation

    Returns:
        Random Hadith data
    """
    async with HadithAPIClient() as client:
        hadith = await client.get_random_hadith()

        if not hadith:
            raise HTTPException(
                status_code=503,
                detail="Could not fetch random Hadith",
            )

        result = {
            "hadith": hadith,
            "source": "Random Hadith API",
        }

        if explain:
            gemini = GeminiService()
            hadith_text = hadith.get("hadithArabic") or hadith.get("text", "")
            explanation = await gemini.explain_hadith(hadith_text, language=language)

            result["explanation"] = explanation
            result["explanation_language"] = language

        return result

