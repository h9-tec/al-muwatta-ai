"""
AI-Powered Islamic Knowledge Assistant Router.

This router provides intelligent AI features using Google Gemini for
Islamic knowledge, questions, explanations, and content generation.
"""

import json

from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.responses import StreamingResponse
from loguru import logger

from ..config import settings
from ..models.schemas import (
    AIResponse,
    IslamicQuestionRequest,
    ThematicStudyRequest,
    TranslationRequest,
)
from ..services import GeminiService, MultiLLMService
from ..services.cache_service import get_cache_service
from ..services.orchestrator_service import get_orchestrator_service

# Optional DSPy import - only needed for /ask-dspy endpoint
try:
    from ..services.dspy_rag_service import get_dspy_rag
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False
    get_dspy_rag = None  # type: ignore

from ..utils.question_classifier import is_fiqh_question

router = APIRouter(prefix="/api/v1/ai", tags=["AI Assistant"])


@router.post("/ask", summary="Ask Islamic questions")
async def ask_islamic_question(request: IslamicQuestionRequest) -> AIResponse:
    """
    Ask any Islamic question and get an AI-generated answer.

    Args:
        request: Question request with language preferences

    Returns:
        AI-generated answer with sources
    """
    try:
        provider = request.provider or "gemini"
        model = request.model
        logger.info(f"AI request using provider={provider}, model={model or 'default'}")

        gemini = GeminiService()
        cache = get_cache_service()
        orchestrator = get_orchestrator_service()

        is_fiqh, category = is_fiqh_question(request.question)
        
        # Use orchestrator to determine if multi-madhab is needed
        should_multi_madhab, reason = await orchestrator.should_use_multi_madhab(request.question)
        
        # Determine target madhabs: only use multi-madhab if orchestrator says so AND user selected madhabs
        target_madhabs = None
        if should_multi_madhab and request.madhabs:
            target_madhabs = request.madhabs
        elif should_multi_madhab and not request.madhabs:
            # Default to all four if fiqh question but no specific madhabs selected
            target_madhabs = ["maliki", "hanafi", "shafii", "hanbali"]
        elif not should_multi_madhab:
            # Not a fiqh question or doesn't need multi-madhab - use single response
            target_madhabs = None
        
        logger.info(
            f"Question classification: is_fiqh={is_fiqh}, should_multi_madhab={should_multi_madhab}, "
            f"reason={reason}, target_madhabs={target_madhabs}"
        )
        
        # Build cache key (question + prefs)
        cache_key = await cache._generate_cache_key(
            "ai:answer",
            request.question,
            language=request.language,
            provider=provider,
            model=model,
            madhabs=tuple(request.madhabs or []),
            as_mode=request.as_mode,
            healing=request.quran_healing_mode,
            web=request.web_search_enabled,
            web_attempts=request.web_search_attempts,
        )

        # Serve from cache if exists
        cached = await cache.get(cache_key)
        if cached:
            return AIResponse(**cached)

        if request.stream:
            if provider != "gemini":
                raise HTTPException(
                    status_code=400, detail="Streaming only supported with Gemini provider"
                )
            if not is_fiqh:
                raise HTTPException(status_code=400, detail="Streaming restricted to fiqh queries")
            try:
                stream_payload = await gemini.stream_fiqh_answer(
                    request.question,
                    language=request.language,
                    madhabs=target_madhabs,
                )
            except Exception as exc:  # pragma: no cover - runtime safeguard
                logger.error(f"Streaming setup failed: {exc}")
                raise HTTPException(status_code=500, detail="Failed to stream answer") from exc

            return StreamingResponse(
                stream_payload["stream"],
                media_type="text/plain; charset=utf-8",
                headers={
                    "X-RAG-Chunks": json.dumps(stream_payload["rag_chunks"])[:4000],
                },
            )

        # Handle Quran Healing mode
        if request.quran_healing_mode:
            healing_content = await orchestrator.get_quran_healing_content(
                user_state=request.question,
                psychological_keywords=None,
            )
            # Use healing content for response
            result = await gemini.answer_with_healing_content(
                request.question,
                language=request.language,
                healing_content=healing_content,
            )
        elif request.as_mode and is_fiqh:
            # AS Mode: Search each madhab separately before answering
            madhab_results = await orchestrator.search_madhabs_separately(
                request.question,
                madhabs=target_madhabs,
                n_results_per_madhab=5,
            )
            # Get Quran/Hadith from cache
            cached_content = await orchestrator.get_quran_hadith_from_cache(
                request.question,
                limit=5,
            )
            web_context = ""
            if request.web_search_enabled:
                # Ensure at least two different queries; cap at 3 attempts
                attempts = min(3, max(1, request.web_search_attempts or 2))
                if target_madhabs and isinstance(target_madhabs, list) and len(target_madhabs) >= 1:
                    web_context = await orchestrator.perform_web_search_by_madhab(
                        request.question,
                        target_madhabs,
                        attempts=attempts,
                    )
                else:
                    web_context = await orchestrator.perform_web_search(
                        request.question, attempts=attempts
                    )

            result = await gemini.answer_with_orchestrated_context(
                request.question,
                language=request.language,
                madhab_results=madhab_results,
                cached_quran_hadith=cached_content,
                web_context=web_context,
            )
        else:
            # Standard flow
            result = await gemini.answer_islamic_question(
                request.question,
                language=request.language,
                madhabs=target_madhabs,
                use_cached_only=not request.quran_healing_mode,  # Use cache for standard mode
            )

        answer_text = result.get("answer")
        rag_chunks = result.get("rag_chunks", [])
        if not answer_text or (is_fiqh and not rag_chunks):
            raise HTTPException(
                status_code=503, detail="Could not generate answer from Maliki sources"
            )

        structured_sources = [
            source for source in result.get("sources", []) if source.get("content")
        ]
        raw_context = result.get("raw_context", {})

        if provider != "gemini":
            service = MultiLLMService(provider=provider, api_key=request.api_key)
            prompt = answer_text
            if raw_context:
                prompt = (
                    "استعن بالسياق التالي للإجابة بدقة ووضوح:\n\n"
                    f"Quran context:\n{raw_context.get('quran', '')}\n\n"
                    f"Hadith context:\n{raw_context.get('hadith', '')}\n\n"
                    f"Fiqh context:\n{raw_context.get('fiqh', '')}\n\n"
                    f"RAG chunks (debug):\n{rag_chunks}\n\n"
                    f"السؤال: {request.question}\n\n"
                    "الإجابة المقترحة:"
                    f"\n{answer_text}\n\n"
                    "طوّر الإجابة السابقة بلغة عربية فصيحة واضحة، مع الحفاظ على الدقة الشرعية وذكر الأدلة ضمن المتن دون ترقيم إن أمكن."
                )

            generated = await service.generate(
                prompt=prompt,
                model=model or "",
                temperature=0.6,
                max_tokens=1500,
            )
            if generated:
                answer_text = generated

        ai_response = AIResponse(
            content=answer_text,
            language=request.language,
            model=model or (provider if provider != "gemini" else settings.gemini_model),
            metadata={
                "question": request.question,
                "provider": provider,
                "model": model,
                "include_sources": request.include_sources,
                "sources": structured_sources,
                "rag_chunks": rag_chunks,
            },
        )

        # Cache the final answer (avoid regeneration). Default TTL from settings.
        await cache.set(cache_key, ai_response.model_dump())

        return ai_response

    except HTTPException:
        raise
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


@router.post("/ask-dspy", summary="Ask using DSPy optimized RAG")
async def ask_with_dspy(request: IslamicQuestionRequest) -> AIResponse:
    """
    Ask Islamic questions using DSPy-optimized RAG pipeline.

    This endpoint uses DSPy's ChainOfThought reasoning with automatic
    prompt optimization for better retrieval and answer quality.

    Args:
        request: Question request with language preferences

    Returns:
        AI-generated answer with reasoning trace and citations
    """
    if not DSPY_AVAILABLE or get_dspy_rag is None:
        raise HTTPException(
            status_code=503,
            detail="DSPy is not installed. Install it with: pip install dspy-ai"
        )

    try:
        logger.info(f"DSPy RAG request: {request.question[:100]}...")

        # Initialize DSPy RAG
        dspy_rag = get_dspy_rag()

        # Check if question is fiqh-related
        is_fiqh, category = is_fiqh_question(request.question)

        if not is_fiqh:
            raise HTTPException(
                status_code=400,
                detail="DSPy RAG is optimized for Maliki fiqh questions only. Use /ask for general Islamic queries.",
            )

        # Get answer with DSPy
        result = dspy_rag.answer_question(
            question=request.question,
            return_context=True,
        )

        # Format sources from context
        sources = []
        if "context" in result:
            for ctx in result["context"]:
                metadata = ctx.get("metadata", {})
                sources.append(
                    {
                        "type": "fiqh",
                        "content": ctx.get("text", "")[:500],
                        "reference": metadata.get("references", ""),
                        "topic": metadata.get("topic", ""),
                        "score": ctx.get("score", 0.0),
                    }
                )

        return AIResponse(
            content=result["answer"],
            language=request.language or "ar",
            model="dspy-cot-gemini-2.0-flash",
            metadata={
                "citations": result.get("citations", ""),
                "reasoning": result.get("reasoning", ""),
                "framework": "dspy",
                "retrieval_count": len(sources),
                "sources": sources,
            },
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"DSPy RAG error: {exc}")
        raise HTTPException(status_code=500, detail=f"DSPy processing failed: {str(exc)}")
