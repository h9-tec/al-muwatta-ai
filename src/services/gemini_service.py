"""
Google Gemini AI Service for Arabic Islamic Content Generation.

This service provides intelligent Arabic content generation, question answering,
and contextual understanding using Google's Gemini models with RAG enhancement.
"""

import asyncio
from typing import TYPE_CHECKING, Any

import google.generativeai as genai
from loguru import logger

from ..config import settings
from ..utils.question_classifier import (
    detect_arabic_dialect,
    get_response_instructions,
    is_arabic_text,
    is_fiqh_question,
    wants_sources,
)

if TYPE_CHECKING:
    pass


class GeminiService:
    """Service for interacting with Google Gemini AI."""

    def __init__(self, enable_rag: bool = True) -> None:
        """
        Initialize the Gemini service with optional RAG.

        Args:
            enable_rag: Whether to enable Maliki fiqh RAG system

        Configures the Gemini API with the provided API key and sets up
        the generative model with optional RAG enhancement.
        """
        try:
            # Only configure Gemini if API key is provided
            if settings.gemini_api_key:
                genai.configure(api_key=settings.gemini_api_key)
                self.model = genai.GenerativeModel(settings.gemini_model)
                logger.info(f"Gemini service initialized with model: {settings.gemini_model}")
            else:
                self.model = None
                logger.warning("Gemini API key not configured - Gemini provider will not be available")

            # Initialize RAG if enabled
            self.rag = None
            if enable_rag:
                try:
                    # Lazy import to avoid heavy deps at import time
                    from .fiqh_rag_service import FiqhRAG  # type: ignore

                    self.rag = FiqhRAG()
                    logger.info("✅ RAG system enabled for multi-madhab fiqh")
                except Exception as rag_error:
                    logger.warning(
                        f"RAG initialization failed (will continue without RAG): {rag_error}"
                    )

            # Lazy import to avoid circular dependency
            from ..api_clients import (
                HadithAPIClient,
                PrayerTimesAPIClient,
                QuranAPIClient,
                QuranComAPIClient,
            )

            self.quran_client = QuranAPIClient()
            self.hadith_client = HadithAPIClient()
            self.quran_com_client = QuranComAPIClient()
            self.prayer_client = PrayerTimesAPIClient()

        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {e}")
            raise

    async def generate_content(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str | None:
        """
        Generate content using Gemini AI.

        Args:
            prompt: The input prompt for content generation
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
            stream: Whether to yield streaming chunks

        Returns:
            Generated content as string or None if generation fails
        """
        try:
            # Check if Gemini model is configured
            if not self.model:
                logger.error("Gemini model not configured - API key missing")
                return None

            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )

            # Offload blocking SDK call to a worker thread to avoid blocking the event loop
            def _generate_sync():
                return self.model.generate_content(
                    prompt,
                    generation_config=generation_config,
                )

            response = await asyncio.to_thread(_generate_sync)

            if response.text:
                logger.info("Content generated successfully")
                return response.text
            logger.warning("No content generated")
            return None

        except Exception as e:
            logger.error(f"Failed to generate content: {e}")
            return None

    async def explain_hadith(
        self,
        hadith_text: str,
        language: str = "arabic",
    ) -> str | None:
        """
        Provide detailed explanation of a Hadith.

        Args:
            hadith_text: The Hadith text to explain
            language: Output language ('arabic' or 'english')

        Returns:
            Detailed explanation or None if generation fails

        Example:
            >>> service = GeminiService()
            >>> explanation = await service.explain_hadith(hadith_text)
            >>> print(explanation)
        """
        lang_instruction = "in Arabic" if language == "arabic" else "in English"

        prompt = f"""
As an Islamic scholar, provide a comprehensive explanation of the following Hadith {lang_instruction}.

Include:
1. Context and background
2. Key lessons and meanings
3. Practical applications in modern life
4. Related Quranic verses or other Hadiths

Hadith:
{hadith_text}
"""

        return await self.generate_content(prompt, temperature=0.5, max_tokens=1500)

    async def explain_quranic_verse(
        self,
        verse_text: str,
        surah_name: str,
        verse_number: int,
        language: str = "arabic",
    ) -> str | None:
        """
        Provide tafsir (explanation) of a Quranic verse.

        Args:
            verse_text: The verse text
            surah_name: Name of the Surah
            verse_number: Verse number
            language: Output language ('arabic' or 'english')

        Returns:
            Tafsir explanation or None if generation fails

        Example:
            >>> service = GeminiService()
            >>> tafsir = await service.explain_quranic_verse(
            ...     verse_text="بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
            ...     surah_name="Al-Fatiha",
            ...     verse_number=1
            ... )
        """
        lang_instruction = "in Arabic" if language == "arabic" else "in English"

        prompt = f"""
As an Islamic scholar specialized in Quranic exegesis (Tafsir), explain the following verse {lang_instruction}.

Surah: {surah_name}
Verse Number: {verse_number}
Verse Text: {verse_text}

Provide:
1. Word-by-word meaning (where relevant)
2. Context of revelation (Asbab al-Nuzul) if known
3. Scholarly interpretations
4. Lessons and guidance for believers
5. Connection to other verses or Hadiths
"""

        return await self.generate_content(prompt, temperature=0.5, max_tokens=2000)

    async def answer_islamic_question(
        self,
        question: str,
        language: str = "arabic",
        madhabs: list[str] | None = None,
        use_cached_only: bool = True,
    ) -> dict[str, Any]:
        """
        Answer Islamic questions with scholarly references.

        Args:
            question: The Islamic question to answer (may include language instruction)
            language: Output language ('arabic' or 'english')

        Returns:
            Detailed answer or None if generation fails

        Example:
            >>> service = GeminiService()
            >>> answer = await service.answer_islamic_question(
            ...     "What are the pillars of Islam?"
            ... )
        """
        # Enhanced language instruction for Arabic
        dialect = detect_arabic_dialect(question) if is_arabic_text(question) else "msa"
        if language == "arabic" or is_arabic_text(question):
            if dialect != "msa":
                lang_instruction = (
                    f"in Arabic, matching the user's dialect ({dialect})."
                    " Maintain colloquial phrasing and tone while keeping jurisprudential terminology precise."
                )
            else:
                lang_instruction = (
                    "in Arabic, using the EXACT same dialect, style, and formality level as the user's question.\n"
                    "If the user writes in formal Modern Standard Arabic (MSA/الفصحى), respond in formal MSA.\n"
                    "If the user writes in colloquial/dialect Arabic (عامية), respond in the SAME colloquial style.\n"
                    "Match their tone - be natural, conversational, and authentic in Arabic."
                )
            language = "arabic"
        else:
            lang_instruction = "in clear, natural English"

        # Detect if this is a fiqh question
        is_fiqh, question_category = is_fiqh_question(question)
        user_wants_sources = wants_sources(question)

        # Get relevant context from RAG ONLY if it's a fiqh question
        rag_context = ""
        rag_chunks: list[dict[str, Any]] = []
        if is_fiqh and self.rag:
            try:
                rag_results = self.rag.search(
                    question,
                    n_results=5,
                    madhabs=madhabs,
                    score_threshold=0.25,
                )
                rag_chunks = rag_results
                rag_context = self.rag.get_relevant_context(
                    question,
                    max_context_length=1500,
                    madhabs=madhabs,
                )
                if rag_context:
                    logger.info(
                        "✅ RAG context retrieved for {} question with {} chunks",
                        question_category,
                        len(rag_results),
                    )
                    logger.debug("RAG chunks: {}", rag_results)
            except Exception as e:
                logger.warning(f"RAG search failed: {e}")

        # Fetch Quranic verses (cache-first, optionally cache-only)
        quran_context = await self._fetch_quran_context(question, cache_only=use_cached_only)

        # Fetch Hadith support (cache-first, optionally cache-only)
        hadith_context = await self._fetch_hadith_context(question, is_fiqh, cache_only=use_cached_only)

        structured_sources = [
            {"type": "quran", "content": quran_context},
            {"type": "hadith", "content": hadith_context},
            {"type": "fiqh", "content": rag_context},
        ]

        # Get appropriate instructions based on question type
        scholar_role = get_response_instructions(is_fiqh, question_category, language)

        # Build prompt differently for fiqh vs non-fiqh questions
        sources_text = "\n".join(
            source["content"] for source in structured_sources if source["content"].strip()
        )

        if is_fiqh and sources_text:
            # Build audience label depending on selected madhabs
            selected_madhabs = madhabs or []
            if selected_madhabs and len(selected_madhabs) == 1:
                school_label = selected_madhabs[0].capitalize()
                school_instruction = f"Direct answer based on {school_label} madhab"
                ref_label = f"Use these verified {school_label} references for your answer (hide citations unless user asks):"
            else:
                school_instruction = (
                    "Present positions per selected madhabs and highlight agreements/differences"
                )
                ref_label = "Use these verified fiqh references from the selected schools (hide citations unless user asks):"

            if user_wants_sources:
                citation_instruction = "IMPORTANT: Include source citations like [Source: Al-Risala] at the end of your answer."
            else:
                citation_instruction = "Do NOT show source citations or references in your answer. Use the sources for knowledge but hide the citations."

            prompt = f"""
{scholar_role}

**{ref_label}**

{sources_text}

{question}

Provide answer {lang_instruction}:
1. {school_instruction}
2. Evidence from Quran and Hadith
3. Practical guidance if relevant

{citation_instruction}

Be accurate, respectful, and respond in the same language/dialect style as the question.
Use proper formatting with headings and bullet points.
"""
        else:
            prompt = f"""
{scholar_role}

**Verified Quranic and Hadith sources retrieved for you:**

{sources_text}

{question}

Provide answer {lang_instruction}:
1. Direct answer based on Quran and authentic Hadith
2. Supporting evidence from Islamic sources
3. Clear explanation and practical guidance if relevant

Be accurate, respectful, and respond in the same language/dialect style as the question.
Use proper formatting with headings and bullet points.
Do NOT mention Maliki madhab, fiqh schools, or jurisprudence unless specifically asked.
Do NOT show source citations unless user explicitly requests them.
"""

            logger.info(
                f"ℹ️ Non-fiqh {question_category} question - using general Islamic knowledge"
            )

        answer = await self.generate_content(prompt, temperature=0.6, max_tokens=2500)
        return {
            "answer": answer,
            "sources": structured_sources,
            "raw_context": {
                "quran": quran_context,
                "hadith": hadith_context,
                "fiqh": rag_context,
            },
            "rag_chunks": rag_chunks,
        }

    async def stream_fiqh_answer(
        self,
        question: str,
        language: str,
        madhabs: list[str] | None = None,
    ) -> dict[str, Any]:
        is_fiqh, category = is_fiqh_question(question)
        if not is_fiqh:
            raise RuntimeError("Streaming is limited to Maliki fiqh questions")

        rag_context = ""
        rag_chunks: list[dict[str, Any]] = []
        if self.rag:
            rag_results = self.rag.search(
                question,
                n_results=5,
                madhabs=madhabs,
                score_threshold=0.25,
            )
            rag_chunks = rag_results
            rag_context = self.rag.get_relevant_context(
                question, max_context_length=1500, madhabs=madhabs
            )
        if not rag_context:
            raise RuntimeError("Maliki fiqh context unavailable")

        dialect = detect_arabic_dialect(question) if is_arabic_text(question) else "msa"
        if language == "arabic" or is_arabic_text(question):
            language = "arabic"
            if dialect != "msa":
                lang_instruction = f"in Arabic matching the user's {dialect} dialect."
            else:
                lang_instruction = "in Arabic matching the user's dialect and tone."
        else:
            lang_instruction = "in clear, natural English"

        scholar_role = get_response_instructions(True, category, language)
        # Build label depending on selected madhabs
        selected_madhabs = madhabs or []
        if selected_madhabs and len(selected_madhabs) == 1:
            school_label = selected_madhabs[0].capitalize()
            school_instruction = f"Direct ruling per {school_label} madhab"
            ref_label = f"Use these verified {school_label} references for your answer:"
        else:
            school_instruction = (
                "Present positions per selected madhabs and highlight agreements/differences"
            )
            ref_label = "Use these verified fiqh references from the selected schools:"

        prompt = f"""
{scholar_role}

**{ref_label}**

{rag_context}

{question}

Provide answer {lang_instruction}:
1. {school_instruction}
2. Supporting evidence from Quran/Hadith
3. Practical guidance

Hide explicit reference citations unless asked. Answer with structured sections.
"""

        generation_config = genai.types.GenerationConfig(
            temperature=0.6,
            max_output_tokens=2000,
        )

        def _sync_stream():
            for chunk in self.model.generate_content(
                prompt,
                generation_config=generation_config,
                stream=True,
            ):
                text = getattr(chunk, "text", "") or ""
                if text:
                    yield text

        async def iterator():
            loop = asyncio.get_running_loop()
            queue: asyncio.Queue[str] = asyncio.Queue()

            def producer():
                try:
                    for piece in _sync_stream():
                        asyncio.run_coroutine_threadsafe(queue.put(piece), loop)
                finally:
                    asyncio.run_coroutine_threadsafe(queue.put(None), loop)

            loop.run_in_executor(None, producer)

            while True:
                item = await queue.get()
                if item is None:
                    break
                yield item

        return {
            "stream": iterator(),
            "rag_chunks": rag_chunks,
        }

    async def generate_thematic_connections(
        self,
        topic: str,
        language: str = "arabic",
    ) -> dict[str, Any] | None:
        """
        Find connections between Quranic verses and Hadiths on a specific topic.

        Args:
            topic: The Islamic topic to explore
            language: Output language ('arabic' or 'english')

        Returns:
            Dictionary with themed connections or None if generation fails

        Example:
            >>> service = GeminiService()
            >>> connections = await service.generate_thematic_connections("patience")
        """
        lang_instruction = "in Arabic" if language == "arabic" else "in English"

        prompt = f"""
Create a thematic study guide on "{topic}" {lang_instruction}.

Provide:
1. Key Quranic verses about this topic (with Surah:Ayah references)
2. Relevant Hadiths (with collection names)
3. How these sources complement each other
4. Practical lessons and applications

Format your response clearly with sections.
"""

        content = await self.generate_content(prompt, temperature=0.6, max_tokens=2000)

        if content:
            return {
                "topic": topic,
                "language": language,
                "content": content,
            }
        return None

    async def summarize_islamic_text(
        self,
        text: str,
        summary_length: str = "medium",
        language: str = "arabic",
    ) -> str | None:
        """
        Summarize Islamic texts while preserving key meanings.

        Args:
            text: The Islamic text to summarize
            summary_length: 'short', 'medium', or 'long'
            language: Output language ('arabic' or 'english')

        Returns:
            Summary or None if generation fails

        Example:
            >>> service = GeminiService()
            >>> summary = await service.summarize_islamic_text(long_text, "short")
        """
        length_tokens = {"short": 200, "medium": 500, "long": 1000}
        max_tokens = length_tokens.get(summary_length, 500)

        lang_instruction = "in Arabic" if language == "arabic" else "in English"

        prompt = f"""
Provide a {summary_length} summary of the following Islamic text {lang_instruction}.

Preserve:
- Key Islamic concepts and terminology
- Main points and arguments
- Important references

Text:
{text}
"""

        return await self.generate_content(prompt, temperature=0.4, max_tokens=max_tokens)

    async def translate_with_context(
        self,
        text: str,
        source_lang: str = "arabic",
        target_lang: str = "english",
    ) -> str | None:
        """
        Translate Islamic texts with cultural and religious context.

        Args:
            text: Text to translate
            source_lang: Source language
            target_lang: Target language

        Returns:
            Contextual translation or None if translation fails

        Example:
            >>> service = GeminiService()
            >>> translation = await service.translate_with_context(
            ...     "الحمد لله رب العالمين",
            ...     "arabic",
            ...     "english"
            ... )
        """
        prompt = f"""
Translate the following Islamic text from {source_lang} to {target_lang}.

Important:
- Preserve religious terminology appropriately
- Maintain the spiritual and cultural context
- Add brief explanatory notes for complex concepts if needed

Text:
{text}
"""

        return await self.generate_content(prompt, temperature=0.3, max_tokens=1000)

    async def generate_daily_reminder(
        self,
        theme: str | None = None,
        language: str = "arabic",
    ) -> str | None:
        """
        Generate a daily Islamic reminder/inspiration.

        Args:
            theme: Optional theme for the reminder
            language: Output language ('arabic' or 'english')

        Returns:
            Inspirational reminder or None if generation fails

        Example:
            >>> service = GeminiService()
            >>> reminder = await service.generate_daily_reminder(theme="gratitude")
        """
        lang_instruction = "in Arabic" if language == "arabic" else "in English"
        theme_text = f"focused on {theme}" if theme else ""

        prompt = f"""
Create a brief, uplifting Islamic daily reminder {theme_text} {lang_instruction}.

Include:
1. A short Quranic verse or Hadith
2. Brief reflection (2-3 sentences)
3. Practical action item

Keep it concise and inspiring.
"""

        return await self.generate_content(prompt, temperature=0.8, max_tokens=500)

    async def verify_hadith_authenticity_guidance(
        self,
        hadith_text: str,
        claimed_source: str,
    ) -> str | None:
        """
        Provide guidance on verifying Hadith authenticity.

        Args:
            hadith_text: The Hadith text
            claimed_source: Claimed collection/source

        Returns:
            Verification guidance or None if generation fails

        Example:
            >>> service = GeminiService()
            >>> guidance = await service.verify_hadith_authenticity_guidance(
            ...     hadith_text,
            ...     "Sahih Bukhari"
            ... )
        """
        prompt = f"""
As an Islamic scholar, provide guidance on verifying this Hadith:

Hadith: {hadith_text}
Claimed Source: {claimed_source}

Discuss:
1. What makes a Hadith authentic (Sahih)
2. How to verify this specific Hadith
3. Importance of chain of narration (Isnad)
4. Recommended resources for verification

Note: This is educational guidance, not a definitive ruling.
"""

        return await self.generate_content(prompt, temperature=0.4, max_tokens=1000)

    async def _fetch_quran_context(self, question: str, cache_only: bool = False) -> str:
        """
        Fetch relevant Quranic verses for the user's question.

        Tries cache first (instant), falls back to API if needed.
        """
        # Try cache first (FAST - no API calls!)
        try:
            from .cached_content_service import get_cached_content_service

            cached_service = get_cached_content_service()

            # Search in cache for Arabic verses
            cached_verses = await cached_service.search_quran_in_cache(
                question, edition="quran-uthmani", limit=3
            )

            if cached_verses:
                logger.info(f"✅ Using {len(cached_verses)} Quran verses from CACHE")
                contexts = []
                for verse in cached_verses:
                    surah_name = verse.get("surah_name", "")
                    ayah_num = verse.get("ayah_number", "")
                    text = verse.get("text", "")
                    contexts.append(f"[Quran {surah_name} {ayah_num}]\n{text}\n")
                return "\n".join(contexts)
        except Exception as exc:
            logger.warning(f"Cache search failed, falling back to API: {exc}")

        if cache_only:
            return ""

        # Fallback to API if cache miss
        try:
            from ..api_clients import QuranAPIClient

            async with QuranAPIClient() as client:
                search_results = await client.search_quran(question, edition="quran-uthmani")
                matches = (
                    search_results.get("matches") if isinstance(search_results, dict) else None
                )
                if matches:
                    contexts = []
                    for match in matches[:3]:
                        text = match.get("text", "")
                        verse_key = match.get("verse_key")
                        contexts.append(f"[Quran {verse_key}]\n{text}\n")
                    return "\n".join(contexts)
        except Exception as exc:
            logger.warning(f"Quran API search failed: {exc}")

        return ""

    async def _fetch_hadith_context(self, question: str, is_fiqh: bool, cache_only: bool = False) -> str:
        """
        Fetch supporting hadith narrations.

        Tries cache first (instant), falls back to API if needed.
        For fiqh questions, prioritizes Muwatta Malik.
        """
        if not question:
            return ""

        # Try cache first (FAST - no API calls!)
        try:
            from .cached_content_service import get_cached_content_service

            cached_service = get_cached_content_service()

            # For Maliki fiqh questions, prioritize Muwatta Malik
            if is_fiqh:
                collections = ["malik", "bukhari", "muslim"]
            else:
                collections = ["bukhari", "muslim", "malik"]

            cached_hadiths = await cached_service.search_hadith_in_cache(
                question, collections=collections, limit=3
            )

            if cached_hadiths:
                logger.info(f"✅ Using {len(cached_hadiths)} Hadiths from CACHE")
                contexts = []
                for hadith in cached_hadiths:
                    collection = hadith.get("collection", "").title()
                    number = hadith.get("number", "")
                    arab = hadith.get("arab", "")
                    text = hadith.get("text", "")
                    contexts.append(f"[Hadith {collection} #{number}]\n{arab}\n{text}\n")
                return "\n".join(contexts)
        except Exception as exc:
            logger.warning(f"Cache search failed, falling back to API: {exc}")

        if cache_only:
            return ""

        # Fallback to API if cache miss
        try:
            from ..api_clients import HadithAPIClient

            async with HadithAPIClient() as client:
                search_results = await client.search_hadith(query=question, limit=3)
                data = search_results.get("data", []) if isinstance(search_results, dict) else []
                contexts = []
                for item in data[:3]:
                    arabic_text = item.get("hadithArabic") or item.get("arab", "")
                    translation = item.get("hadithEnglish") or item.get("id", "")
                    collection = item.get("collection", {}).get("name", "")
                    number = item.get("hadithNumber") or item.get("number")
                    contexts.append(
                        f"[Hadith {collection} #{number}]\n{arabic_text}\n{translation}\n"
                    )
                return "\n".join(contexts)
        except Exception as exc:
            logger.warning(f"Hadith API search failed: {exc}")
        return ""

    async def answer_with_healing_content(
        self,
        question: str,
        language: str = "arabic",
        healing_content: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Answer question using Quran Healing mode with psychological support.

        Args:
            question: User's question
            language: Response language
            healing_content: Dictionary with quran and hadith results for healing

        Returns:
            Response with healing-focused answer
        """
        from ..utils.question_classifier import detect_arabic_dialect, is_arabic_text

        dialect = detect_arabic_dialect(question) if is_arabic_text(question) else "msa"
        if language == "arabic" or is_arabic_text(question):
            lang_instruction = (
                "in Arabic, matching the user's dialect and tone"
                if dialect == "msa"
                else f"in Arabic matching the user's {dialect} dialect"
            )
            language = "arabic"
        else:
            lang_instruction = "in clear, natural English"

        # Format healing content
        quran_texts = []
        for q in (healing_content or {}).get("quran", [])[:5]:
            verse_key = q.get("surah", {}).get("number", "") if isinstance(q.get("surah"), dict) else ""
            verse_num = q.get("numberInSurah", "")
            text = q.get("text", "")
            if text:
                quran_texts.append(f"[Quran {verse_key}:{verse_num}]\n{text}\n")

        hadith_texts = []
        for h in (healing_content or {}).get("hadith", [])[:5]:
            collection = h.get("collection", "").title()
            number = h.get("number", "")
            arab = h.get("arab", "")
            text = h.get("text", "")
            if arab or text:
                hadith_texts.append(f"[Hadith {collection} #{number}]\n{arab}\n{text}\n")

        healing_sources = "\n".join(quran_texts + hadith_texts)

        prompt = f"""
You are a compassionate Islamic counselor providing spiritual and psychological healing through Quran and Hadith.

**Healing Sources (DO NOT MODIFY - Return exactly as provided):**

{healing_sources}

**User's Question/State:**
{question}

Provide a compassionate, healing response {lang_instruction}:
1. Acknowledge the user's feelings with empathy
2. Present the healing verses/hadiths EXACTLY as provided above (do not paraphrase or modify)
3. Provide gentle reflection and comfort
4. Offer practical spiritual guidance

Be warm, understanding, and supportive. Return Quran and Hadith texts exactly as shown above.
"""

        answer = await self.generate_content(prompt, temperature=0.7, max_tokens=2000)

        return {
            "answer": answer or "",
            "sources": [
                {"type": "quran", "content": "\n".join(quran_texts)},
                {"type": "hadith", "content": "\n".join(hadith_texts)},
            ],
            "raw_context": {
                "quran": "\n".join(quran_texts),
                "hadith": "\n".join(hadith_texts),
                "fiqh": "",
            },
            "rag_chunks": [],
        }

    async def answer_with_orchestrated_context(
        self,
        question: str,
        language: str = "arabic",
        madhab_results: dict[str, list[dict[str, Any]]] | None = None,
        cached_quran_hadith: dict[str, Any] | None = None,
        web_context: str | None = None,
    ) -> dict[str, Any]:
        """
        Answer question using AS Mode with separate madhab searches and cached content.

        Args:
            question: User's question
            language: Response language
            madhab_results: Dictionary mapping madhab keys to their search results
            cached_quran_hadith: Dictionary with quran and hadith from cache

        Returns:
            Response with orchestrated answer
        """
        from ..utils.question_classifier import detect_arabic_dialect, is_arabic_text, get_response_instructions

        dialect = detect_arabic_dialect(question) if is_arabic_text(question) else "msa"
        if language == "arabic" or is_arabic_text(question):
            lang_instruction = (
                "in Arabic, matching the user's dialect and tone"
                if dialect == "msa"
                else f"in Arabic matching the user's {dialect} dialect"
            )
            language = "arabic"
        else:
            lang_instruction = "in clear, natural English"

        is_fiqh, category = is_fiqh_question(question)
        scholar_role = get_response_instructions(is_fiqh, category, language)

        # Format madhab results
        madhab_contexts = []
        for madhab, results in (madhab_results or {}).items():
            if results:
                madhab_text = f"\n=== {madhab.upper()} MADHAB RESULTS ===\n"
                for result in results[:3]:  # Top 3 per madhab
                    text = result.get("text", "")
                    metadata = result.get("metadata", {})
                    ref = metadata.get("references", "")
                    if text:
                        madhab_text += f"{text}\n"
                        if ref:
                            madhab_text += f"Reference: {ref}\n"
                madhab_contexts.append(madhab_text)

        # Format Quran/Hadith from cache (DO NOT MODIFY)
        quran_texts = []
        for q in (cached_quran_hadith or {}).get("quran", []):
            verse_key = q.get("surah", {}).get("number", "") if isinstance(q.get("surah"), dict) else ""
            verse_num = q.get("numberInSurah", "")
            text = q.get("text", "")
            if text:
                quran_texts.append(f"[Quran {verse_key}:{verse_num}]\n{text}\n")

        hadith_texts = []
        for h in (cached_quran_hadith or {}).get("hadith", []):
            collection = h.get("collection", "").title()
            number = h.get("number", "")
            arab = h.get("arab", "")
            text = h.get("text", "")
            if arab or text:
                hadith_texts.append(f"[Hadith {collection} #{number}]\n{arab}\n{text}\n")

        web_section = f"\n\n### Web Context (scraped)\n\n{web_context}\n" if web_context else ""

        all_context = "\n".join(madhab_contexts + quran_texts + hadith_texts) + web_section

        prompt = f"""
{scholar_role}

**Verified Sources from AS Mode Search (DO NOT MODIFY Quran/Hadith - Return exactly as shown):**

{all_context}

**Question:**
{question}

Provide answer {lang_instruction}:
1. Search results from each madhab (present separately)
2. Quran verses EXACTLY as shown above (do not modify or paraphrase)
3. Hadiths EXACTLY as shown above (do not modify or paraphrase)
4. Comprehensive analysis comparing madhab positions if multiple

IMPORTANT:
- Return Quran and Hadith texts EXACTLY as provided - do not modify or paraphrase
- Present madhab results clearly by school
- Hide citations unless user explicitly asks
"""

        answer = await self.generate_content(prompt, temperature=0.6, max_tokens=3000)

        # Flatten madhab results for rag_chunks
        rag_chunks = []
        for madhab, results in (madhab_results or {}).items():
            rag_chunks.extend(results)

        return {
            "answer": answer or "",
            "sources": [
                {"type": "quran", "content": "\n".join(quran_texts)},
                {"type": "hadith", "content": "\n".join(hadith_texts)},
                {"type": "fiqh", "content": "\n".join(madhab_contexts)},
                {"type": "web", "content": web_context or ""},
            ],
            "raw_context": {
                "quran": "\n".join(quran_texts),
                "hadith": "\n".join(hadith_texts),
                "fiqh": "\n".join(madhab_contexts),
                "web": web_context or "",
            },
            "rag_chunks": rag_chunks,
        }
