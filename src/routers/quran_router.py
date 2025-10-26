"""
Quran API Router.

This router provides endpoints for accessing Quranic verses, translations, and tafsir.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from ..api_clients import QuranAPIClient, QuranComAPIClient
from ..services import GeminiService
from ..models.schemas import QuranVerseRequest, QuranVerseResponse

router = APIRouter(prefix="/api/v1/quran", tags=["Quran"])


@router.get("/editions", summary="Get all Quran editions")
async def get_quran_editions(
    language: str = Query(None, description="Filter by language"),
    format_type: str = Query(None, description="Filter by format (text/audio)"),
) -> List[Dict[str, Any]]:
    """
    Retrieve all available Quran editions and translations.

    Args:
        language: Filter by language code (e.g., 'en', 'ar')
        format_type: Filter by format ('text' or 'audio')

    Returns:
        List of available editions
    """
    async with QuranAPIClient() as client:
        editions = await client.get_editions(
            format_type=format_type,
            language=language,
        )
        if editions:
            return editions

    async with QuranComAPIClient() as quran_com:
        chapters = await quran_com.get_chapters()
        return chapters or []


@router.get("/surahs/{surah_number}", summary="Get complete Surah")
async def get_surah(
    surah_number: int,
    edition: str = Query("quran-uthmani", description="Quran edition"),
    explain: bool = Query(False, description="Get AI tafsir for each verse"),
    language: str = Query("english", description="Explanation language"),
) -> Dict[str, Any]:
    """
    Retrieve a complete Surah with optional AI tafsir.

    Args:
        surah_number: Surah number (1-114)
        edition: Edition identifier
        explain: Whether to include AI tafsir
        language: Language for tafsir

    Returns:
        Surah data with all verses
    """
    async with QuranAPIClient() as client:
        surah = await client.get_surah(surah_number, edition=edition)

        if not surah:
            raise HTTPException(
                status_code=404,
                detail=f"Surah {surah_number} not found",
            )

        result = {
            "surah": surah,
            "source": "alquran.cloud API",
        }

        if explain and surah.get("ayahs"):
            gemini = GeminiService()
            explanations = []

            # Provide explanation for the first few verses as example
            for ayah in surah["ayahs"][:3]:  # First 3 verses
                tafsir = await gemini.explain_quranic_verse(
                    verse_text=ayah.get("text", ""),
                    surah_name=surah.get("englishName", ""),
                    verse_number=ayah.get("numberInSurah", 0),
                    language=language,
                )
                explanations.append({
                    "verse_number": ayah.get("numberInSurah"),
                    "tafsir": tafsir,
                })

            result["sample_tafsir"] = explanations
            result["tafsir_language"] = language

        return result


@router.get("/ayahs/{ayah_reference}", summary="Get specific Ayah")
async def get_ayah(
    ayah_reference: str,
    edition: str = Query("quran-uthmani", description="Quran edition"),
    explain: bool = Query(False, description="Get AI tafsir"),
    language: str = Query("english", description="Explanation language"),
) -> Dict[str, Any]:
    """
    Retrieve a specific Ayah by reference (e.g., '2:255' for Ayat al-Kursi).

    Args:
        ayah_reference: Ayah reference in format 'surah:verse'
        edition: Edition identifier
        explain: Whether to include AI tafsir
        language: Language for tafsir

    Returns:
        Ayah data with optional tafsir
    """
    async with QuranAPIClient() as client:
        ayah = await client.get_ayah(ayah_reference, edition=edition)

        if not ayah:
            raise HTTPException(
                status_code=404,
                detail=f"Ayah {ayah_reference} not found",
            )

        result = {
            "ayah": ayah,
            "source": "alquran.cloud API",
        }

        if explain:
            gemini = GeminiService()
            tafsir = await gemini.explain_quranic_verse(
                verse_text=ayah.get("text", ""),
                surah_name=ayah.get("surah", {}).get("englishName", ""),
                verse_number=ayah.get("numberInSurah", 0),
                language=language,
            )

            result["tafsir"] = tafsir
            result["tafsir_language"] = language

        return result


@router.get("/juz/{juz_number}", summary="Get Juz")
async def get_juz(
    juz_number: int,
    edition: str = Query("quran-uthmani", description="Quran edition"),
) -> Dict[str, Any]:
    """
    Retrieve a specific Juz (part) of the Quran.

    Args:
        juz_number: Juz number (1-30)
        edition: Edition identifier

    Returns:
        Juz data with all ayahs
    """
    async with QuranAPIClient() as client:
        juz = await client.get_juz(juz_number, edition=edition)

        if not juz:
            raise HTTPException(
                status_code=404,
                detail=f"Juz {juz_number} not found",
            )

        return {
            "juz": juz,
            "source": "alquran.cloud API",
        }


@router.get("/pages/{page_number}", summary="Get Quran page")
async def get_page(
    page_number: int,
    edition: str = Query("quran-uthmani", description="Quran edition"),
) -> Dict[str, Any]:
    """
    Retrieve a specific page of the Quran.

    Args:
        page_number: Page number (1-604)
        edition: Edition identifier

    Returns:
        Page data with all ayahs
    """
    async with QuranAPIClient() as client:
        page = await client.get_page(page_number, edition=edition)

        if not page:
            raise HTTPException(
                status_code=404,
                detail=f"Page {page_number} not found",
            )

        return {
            "page": page,
            "source": "alquran.cloud API",
        }


@router.get("/search", summary="Search Quran")
async def search_quran(
    query: str = Query(..., description="Search query"),
    surah: int = Query(None, description="Limit to specific Surah"),
    edition: str = Query("quran-uthmani", description="Edition to search"),
) -> Dict[str, Any]:
    """
    Search for verses in the Quran.

    Args:
        query: Search query (Arabic or transliteration)
        surah: Optional Surah number to limit search
        edition: Edition to search in

    Returns:
        Search results with matching verses
    """
    async with QuranAPIClient() as client:
        results = await client.search_quran(query, surah=surah, edition=edition)
        if results.get("matches"):
            return {
                "results": results,
                "query": query,
                "source": "alquran.cloud API",
            }

    async with QuranComAPIClient() as quran_com:
        quran_com_results = await quran_com.get_chapters()
        return {
            "results": quran_com_results,
            "query": query,
            "source": "quran.com API",
        }


@router.get(
    "/surahs/{surah_number}/multiple-editions",
    summary="Get Surah with multiple translations",
)
async def get_surah_multiple_editions(
    surah_number: int,
    editions: str = Query(
        "quran-uthmani,en.sahih",
        description="Comma-separated edition identifiers",
    ),
) -> Dict[str, Any]:
    """
    Retrieve a Surah with multiple editions/translations at once.

    Args:
        surah_number: Surah number (1-114)
        editions: Comma-separated list of edition identifiers

    Returns:
        Surah data in multiple editions
    """
    editions_list = [e.strip() for e in editions.split(",")]

    async with QuranAPIClient() as client:
        surah_data = await client.get_surah_with_multiple_editions(
            surah_number,
            editions_list,
        )

        if not surah_data:
            raise HTTPException(
                status_code=404,
                detail=f"Surah {surah_number} not found",
            )

        return {
            "surah": surah_data,
            "editions": editions_list,
            "source": "alquran.cloud API",
        }

