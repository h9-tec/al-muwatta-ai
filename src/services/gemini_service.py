"""
Google Gemini AI Service for Arabic Islamic Content Generation.

This service provides intelligent Arabic content generation, question answering,
and contextual understanding using Google's Gemini models with RAG enhancement.
"""

from typing import Any, Dict, List, Optional
import google.generativeai as genai
from loguru import logger

from ..config import settings
from .rag_service import MalikiFiqhRAG
from ..utils.question_classifier import (
    is_fiqh_question,
    get_response_instructions,
    wants_sources,
)
from ..api_clients import QuranAPIClient, QuranComAPIClient, HadithAPIClient, PrayerTimesAPIClient


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
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel(settings.gemini_model)
            logger.info(f"Gemini service initialized with model: {settings.gemini_model}")

            # Initialize RAG if enabled
            self.rag = None
            if enable_rag:
                try:
                    self.rag = MalikiFiqhRAG()
                    logger.info("✅ RAG system enabled for Maliki fiqh")
                except Exception as rag_error:
                    logger.warning(f"RAG initialization failed (will continue without RAG): {rag_error}")

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
    ) -> Optional[str]:
        """
        Generate content using Gemini AI.

        Args:
            prompt: The input prompt for content generation
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate

        Returns:
            Generated content as string or None if generation fails

        Example:
            >>> service = GeminiService()
            >>> content = await service.generate_content("Explain the concept of Tawheed")
            >>> print(content)
        """
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
            )

            if response.text:
                logger.info("Content generated successfully")
                return response.text
            else:
                logger.warning("No content generated")
                return None

        except Exception as e:
            logger.error(f"Failed to generate content: {e}")
            return None

    async def explain_hadith(
        self,
        hadith_text: str,
        language: str = "arabic",
    ) -> Optional[str]:
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
    ) -> Optional[str]:
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
    ) -> Optional[str]:
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
        if language == "arabic":
            lang_instruction = """in Arabic, using the EXACT same dialect, style, and formality level as the user's question. 
If the user writes in formal Modern Standard Arabic (MSA/الفصحى), respond in formal MSA. 
If the user writes in colloquial/dialect Arabic (عامية), respond in the SAME colloquial style.
Match their tone - be natural, conversational, and authentic in Arabic."""
        else:
            lang_instruction = "in clear, natural English"

        # Detect if this is a fiqh question
        is_fiqh, question_category = is_fiqh_question(question)
        user_wants_sources = wants_sources(question)
        
        # Get relevant context from RAG ONLY if it's a fiqh question
        rag_context = ""
        if is_fiqh and self.rag:
            try:
                rag_context = self.rag.get_relevant_context(question, max_context_length=1500)
                if rag_context:
                    logger.info(f"✅ RAG context retrieved for {question_category} question")
            except Exception as e:
                logger.warning(f"RAG search failed: {e}")

        # Fetch Quranic verses from live API when question references specific ayah
        quran_context = await self._fetch_quran_context(question)

        # Fetch Hadith support for non-fiqh questions
        hadith_context = await self._fetch_hadith_context(question, is_fiqh)

        structured_sources = [
            {"type": "quran", "content": quran_context},
            {"type": "hadith", "content": hadith_context},
            {"type": "fiqh", "content": rag_context},
        ]
        
        # Get appropriate instructions based on question type
        scholar_role = get_response_instructions(is_fiqh, question_category, language)

        # Build prompt differently for fiqh vs non-fiqh questions
        sources_text = "\n".join(source["content"] for source in structured_sources if source["content"].strip())

        if is_fiqh and sources_text:
            if user_wants_sources:
                citation_instruction = "IMPORTANT: Include source citations like [Source: Al-Risala] at the end of your answer."
            else:
                citation_instruction = "Do NOT show source citations or references in your answer. Use the sources for knowledge but hide the citations."
            
            prompt = f"""
{scholar_role}

**Use these verified Maliki references for your answer (hide citations unless user asks):**

{sources_text}

{question}

Provide answer {lang_instruction}:
1. Direct answer based on Maliki madhab
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

            logger.info(f"ℹ️ Non-fiqh {question_category} question - using general Islamic knowledge")

        return await self.generate_content(prompt, temperature=0.6, max_tokens=2500)

    async def generate_thematic_connections(
        self,
        topic: str,
        language: str = "arabic",
    ) -> Optional[Dict[str, Any]]:
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
    ) -> Optional[str]:
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
    ) -> Optional[str]:
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
        theme: Optional[str] = None,
        language: str = "arabic",
    ) -> Optional[str]:
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
    ) -> Optional[str]:
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

    async def _fetch_quran_context(self, question: str) -> str:
        """Fetch relevant Quranic verses for the user's question."""
        try:
            async with QuranAPIClient() as client:
                search_results = await client.search_quran(question, edition="quran-uthmani")
                matches = search_results.get("matches") if isinstance(search_results, dict) else None
                if matches:
                    contexts = []
                    for match in matches[:3]:
                        text = match.get("text", "")
                        verse_key = match.get("verse_key")
                        contexts.append(f"[Quran {verse_key}]\n{text}\n")
                    return "\n".join(contexts)
        except Exception as exc:
            logger.warning(f"Quran Cloud search failed: {exc}")

        try:
            async with QuranComAPIClient() as quran_com:
                response = await quran_com.search(question)
                verses = response.get("search", {}).get("results", []) if isinstance(response, dict) else []
                contexts = []
                for verse in verses[:3]:
                    verse_key = verse.get("verse_key")
                    text = verse.get("text") or ""
                    contexts.append(f"[Quran {verse_key}]\n{text}\n")
                return "\n".join(contexts)
        except Exception as exc:
            logger.warning(f"Quran.com search failed: {exc}")
        return ""

    async def _fetch_hadith_context(self, question: str, is_fiqh: bool) -> str:
        """Fetch supporting hadith narrations."""
        if not question:
            return ""

        try:
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
            logger.warning(f"Hadith search failed: {exc}")
        return ""

