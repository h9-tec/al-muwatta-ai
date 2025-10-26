"""
AI-Powered Islamic Knowledge Assistant Router.

This router provides intelligent AI features using Google Gemini for
Islamic knowledge, questions, explanations, and content generation.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body
from loguru import logger

from ..services import GeminiService
from ..models.schemas import (
    IslamicQuestionRequest,
    ThematicStudyRequest,
    TranslationRequest,
    AIResponse,
)

router = APIRouter(prefix="/api/v1/ai", tags=["AI Assistant"])


@router.post("/ask", summary="Ask Islamic questions", response_model=AIResponse)
async def ask_islamic_question(request: IslamicQuestionRequest) -> AIResponse:
    """
    Ask any Islamic question and get an AI-generated answer.

    Args:
        request: Question request with language preferences

    Returns:
        AI-generated answer with sources
    """
    try:
        gemini = GeminiService()

        answer, structured_sources = await gemini.answer_islamic_question(
            request.question,
            language=request.language,
        )

        if not answer:
            raise HTTPException(
                status_code=503,
                detail="Could not generate answer",
            )

        return AIResponse(
            content=answer,
            language=request.language,
            model="gemini-2.0-flash-exp",
            metadata={
                "question": request.question,
                "include_sources": request.include_sources,
                "sources": structured_sources,
            },
        )

    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/thematic-study",
    summary="Generate thematic Islamic study",
    response_model=AIResponse,
)
async def generate_thematic_study(request: ThematicStudyRequest) -> AIResponse:
    """
    Generate a comprehensive thematic study on an Islamic topic.

    Args:
        request: Thematic study request with topic and preferences

    Returns:
        AI-generated thematic study with verses and hadiths
    """
    try:
        gemini = GeminiService()

        study = await gemini.generate_thematic_connections(
            request.topic,
            language=request.language,
        )

        if not study:
            raise HTTPException(
                status_code=503,
                detail="Could not generate thematic study",
            )

        return AIResponse(
            content=study.get("content", ""),
            language=request.language,
            model="gemini-2.0-flash-exp",
            metadata={
                "topic": request.topic,
                "include_verses": request.include_verses,
                "include_hadiths": request.include_hadiths,
            },
        )

    except Exception as e:
        logger.error(f"Error generating thematic study: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/translate",
    summary="Translate Islamic text with context",
    response_model=AIResponse,
)
async def translate_islamic_text(request: TranslationRequest) -> AIResponse:
    """
    Translate Islamic text with cultural and religious context.

    Args:
        request: Translation request with text and language preferences

    Returns:
        Contextual translation
    """
    try:
        gemini = GeminiService()

        translation = await gemini.translate_with_context(
            request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
        )

        if not translation:
            raise HTTPException(
                status_code=503,
                detail="Could not translate text",
            )

        return AIResponse(
            content=translation,
            language=request.target_lang,
            model="gemini-2.0-flash-exp",
            metadata={
                "original_text": request.text,
                "source_language": request.source_lang,
                "target_language": request.target_lang,
            },
        )

    except Exception as e:
        logger.error(f"Error translating text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/daily-reminder", summary="Get daily Islamic reminder")
async def get_daily_reminder(
    theme: str = Query(None, description="Optional theme for the reminder"),
    language: str = Query("english", description="Language"),
) -> AIResponse:
    """
    Get a daily Islamic reminder/inspiration.

    Args:
        theme: Optional theme (e.g., 'gratitude', 'patience')
        language: Response language

    Returns:
        Daily Islamic reminder
    """
    try:
        gemini = GeminiService()

        reminder = await gemini.generate_daily_reminder(
            theme=theme,
            language=language,
        )

        if not reminder:
            raise HTTPException(
                status_code=503,
                detail="Could not generate daily reminder",
            )

        return AIResponse(
            content=reminder,
            language=language,
            model="gemini-2.0-flash-exp",
            metadata={"theme": theme},
        )

    except Exception as e:
        logger.error(f"Error generating daily reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize", summary="Summarize Islamic text")
async def summarize_islamic_text(
    text: str = Body(..., description="Text to summarize"),
    summary_length: str = Body("medium", description="Summary length"),
    language: str = Body("english", description="Output language"),
) -> AIResponse:
    """
    Summarize Islamic texts while preserving key meanings.

    Args:
        text: Text to summarize
        summary_length: 'short', 'medium', or 'long'
        language: Output language

    Returns:
        Summary of the text
    """
    try:
        gemini = GeminiService()

        summary = await gemini.summarize_islamic_text(
            text,
            summary_length=summary_length,
            language=language,
        )

        if not summary:
            raise HTTPException(
                status_code=503,
                detail="Could not generate summary",
            )

        return AIResponse(
            content=summary,
            language=language,
            model="gemini-2.0-flash-exp",
            metadata={
                "summary_length": summary_length,
                "original_length": len(text),
            },
        )

    except Exception as e:
        logger.error(f"Error summarizing text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify-hadith", summary="Get Hadith verification guidance")
async def verify_hadith_authenticity(
    hadith_text: str = Body(..., description="Hadith text"),
    claimed_source: str = Body(..., description="Claimed source/collection"),
) -> AIResponse:
    """
    Get guidance on verifying Hadith authenticity.

    Args:
        hadith_text: The Hadith text to verify
        claimed_source: Claimed collection or source

    Returns:
        Verification guidance
    """
    try:
        gemini = GeminiService()

        guidance = await gemini.verify_hadith_authenticity_guidance(
            hadith_text,
            claimed_source,
        )

        if not guidance:
            raise HTTPException(
                status_code=503,
                detail="Could not generate verification guidance",
            )

        return AIResponse(
            content=guidance,
            language="english",
            model="gemini-2.0-flash-exp",
            metadata={
                "hadith_text": hadith_text[:100] + "...",
                "claimed_source": claimed_source,
            },
        )

    except Exception as e:
        logger.error(f"Error generating verification guidance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain-verse", summary="Get Quranic verse explanation")
async def explain_quranic_verse(
    verse_text: str = Body(..., description="Verse text"),
    surah_name: str = Body(..., description="Surah name"),
    verse_number: int = Body(..., description="Verse number"),
    language: str = Body("english", description="Explanation language"),
) -> AIResponse:
    """
    Get detailed tafsir (explanation) of a Quranic verse.

    Args:
        verse_text: The verse text
        surah_name: Name of the Surah
        verse_number: Verse number
        language: Output language

    Returns:
        Detailed tafsir
    """
    try:
        gemini = GeminiService()

        tafsir = await gemini.explain_quranic_verse(
            verse_text,
            surah_name,
            verse_number,
            language=language,
        )

        if not tafsir:
            raise HTTPException(
                status_code=503,
                detail="Could not generate tafsir",
            )

        return AIResponse(
            content=tafsir,
            language=language,
            model="gemini-2.0-flash-exp",
            metadata={
                "surah_name": surah_name,
                "verse_number": verse_number,
            },
        )

    except Exception as e:
        logger.error(f"Error generating tafsir: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain-hadith", summary="Get Hadith explanation")
async def explain_hadith(
    hadith_text: str = Body(..., description="Hadith text"),
    language: str = Body("english", description="Explanation language"),
) -> AIResponse:
    """
    Get detailed explanation of a Hadith.

    Args:
        hadith_text: The Hadith text
        language: Output language

    Returns:
        Detailed Hadith explanation
    """
    try:
        gemini = GeminiService()

        explanation = await gemini.explain_hadith(hadith_text, language=language)

        if not explanation:
            raise HTTPException(
                status_code=503,
                detail="Could not generate explanation",
            )

        return AIResponse(
            content=explanation,
            language=language,
            model="gemini-2.0-flash-exp",
            metadata={"hadith_preview": hadith_text[:100] + "..."},
        )

    except Exception as e:
        logger.error(f"Error explaining Hadith: {e}")
        raise HTTPException(status_code=500, detail=str(e))

