"""
Orchestrator Service for Intelligent Multi-Madhab Fiqh Responses.

This service orchestrates responses by:
1. Classifying questions to determine if multi-madhab is needed
2. Searching each madhab separately before answering
3. Using Quran/Hadith from cache without modification
4. Providing Quran Healing mode for psychological support
"""

from __future__ import annotations

from typing import Any

from loguru import logger

from ..services.cached_content_service import get_cached_content_service
from ..services.fiqh_rag_service import FiqhRAG, get_fiqh_rag
from ..utils.question_classifier import is_fiqh_question

MADHAB_KEYS = ["maliki", "hanafi", "shafii", "hanbali"]


class OrchestratorService:
    """Orchestrates multi-madhab search and response generation."""

    def __init__(self) -> None:
        """Initialize orchestrator with RAG and cache services."""
        self.rag = get_fiqh_rag()
        self.cache_service = get_cached_content_service()
        # Lazy import to avoid circular dependency
        self._gemini_service = None

    async def search_madhabs_separately(
        self,
        query: str,
        madhabs: list[str] | None = None,
        n_results_per_madhab: int = 5,
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Search each madhab collection separately and return results per madhab.

        Args:
            query: Search query
            madhabs: List of madhabs to search (default: all four)
            n_results_per_madhab: Number of results per madhab

        Returns:
            Dictionary mapping madhab keys to their search results
        """
        selected_madhabs = madhabs or MADHAB_KEYS

        # Normalize madhab names
        normalized = []
        for m in selected_madhabs:
            from ..services.fiqh_rag_service import normalize_madhab_name

            norm = normalize_madhab_name(m)
            if norm:
                normalized.append(norm)

        if not normalized:
            normalized = MADHAB_KEYS

        results_by_madhab: dict[str, list[dict[str, Any]]] = {}

        # Search each madhab separately
        for madhab in normalized:
            try:
                madhab_results = self.rag.search(
                    query,
                    n_results=n_results_per_madhab,
                    madhabs=[madhab],
                    score_threshold=0.3,
                )
                results_by_madhab[madhab] = madhab_results
                logger.info(
                    f"✅ Searched {madhab} madhab: found {len(madhab_results)} results"
                )
            except Exception as e:
                logger.error(f"Failed to search {madhab} madhab: {e}")
                results_by_madhab[madhab] = []

        return results_by_madhab

    async def get_quran_hadith_from_cache(
        self,
        query: str,
        limit: int = 5,
    ) -> dict[str, Any]:
        """
        Get Quran and Hadith from cache without modification.

        Args:
            query: Search query
            limit: Maximum results per type

        Returns:
            Dictionary with quran_results and hadith_results
        """
        quran_results = await self.cache_service.search_quran_in_cache(
            query, limit=limit
        )
        hadith_results = await self.cache_service.search_hadith_in_cache(
            query, limit=limit
        )

        return {
            "quran": quran_results,
            "hadith": hadith_results,
        }

    async def get_quran_healing_content(
        self,
        user_state: str | None = None,
        psychological_keywords: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get Quranic verses and Hadiths for psychological healing/comfort.

        Args:
            user_state: User's emotional/psychological state
            psychological_keywords: Keywords describing psychological needs

        Returns:
            Healing content from Quran and Hadith
        """
        # Common healing-related keywords
        healing_keywords = psychological_keywords or []
        if user_state:
            healing_keywords.append(user_state)

        # Default healing topics if none provided
        if not healing_keywords:
            healing_keywords = [
                "patience",
                "comfort",
                "relief",
                "peace",
                "mercy",
                "forgiveness",
                "hope",
                "strength",
            ]

        all_quran = []
        all_hadith = []

        for keyword in healing_keywords:
            quran_results = await self.cache_service.search_quran_in_cache(
                keyword, limit=3
            )
            hadith_results = await self.cache_service.search_hadith_in_cache(
                keyword, limit=3
            )

            all_quran.extend(quran_results)
            all_hadith.extend(hadith_results)

        # Deduplicate by content
        seen_quran = set()
        unique_quran = []
        for q in all_quran:
            content_key = q.get("text", "")
            if content_key and content_key not in seen_quran:
                seen_quran.add(content_key)
                unique_quran.append(q)

        seen_hadith = set()
        unique_hadith = []
        for h in all_hadith:
            content_key = h.get("arab", "") + h.get("text", "")
            if content_key and content_key not in seen_hadith:
                seen_hadith.add(content_key)
                unique_hadith.append(h)

        return {
            "quran": unique_quran[:10],  # Limit to 10 most relevant
            "hadith": unique_hadith[:10],
        }

    async def should_use_multi_madhab(self, question: str) -> tuple[bool, str]:
        """
        Determine if question requires multi-madhab response using LLM analysis.

        Args:
            question: User's question

        Returns:
            Tuple of (should_use_multi_madhab: bool, reason: str)
        """
        # Lazy load Gemini service
        if self._gemini_service is None:
            from ..services.gemini_service import GeminiService

            self._gemini_service = GeminiService()

        # First check if it's a fiqh question at all
        is_fiqh, category = is_fiqh_question(question)
        if not is_fiqh:
            return (
                False,
                f"Question is about {category}, not fiqh. Multi-madhab only for fiqh questions.",
            )

        # Use LLM to analyze if multi-madhab perspective is needed
        analysis_prompt = f"""
You are an expert Islamic scholar analyzing user questions to determine if they require a multi-madhab (multi-school) fiqh response.

**Question to analyze:**
"{question}"

**Context:**
In Islamic jurisprudence (fiqh), there are four major Sunni schools (madhabs):
1. Maliki - Founded by Imam Malik
2. Hanafi - Founded by Imam Abu Hanifa
3. Shafi'i - Founded by Imam Shafi'i
4. Hanbali - Founded by Imam Ahmad ibn Hanbal

**When to use multi-madhab response:**
- General fiqh questions that could have different rulings across schools
- Questions implicitly asking about Islamic law without specifying a school
- Questions about differences between schools
- Questions that would benefit from seeing multiple perspectives

**When NOT to use multi-madhab response:**
- Simple greetings, casual conversation, non-religious questions
- Questions explicitly about a single specific madhab (e.g., "What does Maliki say about...")
- Questions about Quran recitation, Hadith narration, or general Islamic knowledge
- Questions that are clearly not about Islamic law/jurisprudence

**Your task:**
Analyze the question and respond with ONLY a JSON object in this exact format:
{{
    "needs_multi_madhab": true/false,
    "reason": "Brief explanation of why multi-madhab is or isn't needed (1-2 sentences)"
}}

Be precise and thoughtful. Consider the nuance of the question.
"""

        try:
            # Get LLM classification
            response_text = await self._gemini_service.generate_content(
                analysis_prompt, temperature=0.3, max_tokens=200
            )

            # Parse JSON response
            import json

            # Try to parse entire response as JSON first
            try:
                result = json.loads(response_text.strip())
                needs_multi = result.get("needs_multi_madhab", False)
                reason = result.get("reason", "LLM analysis completed")
                logger.info(
                    f"Orchestrator LLM analysis: needs_multi_madhab={needs_multi}, reason={reason}"
                )
                return (needs_multi, reason)
            except json.JSONDecodeError:
                # Try to extract JSON object from response
                import re
                # Find JSON object with proper brace matching
                brace_count = 0
                start_idx = -1
                json_match = None
                for i, char in enumerate(response_text):
                    if char == '{':
                        if brace_count == 0:
                            start_idx = i
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0 and start_idx != -1:
                            json_match = response_text[start_idx:i+1]
                            break
                
                if json_match:
                    try:
                        result = json.loads(json_match)
                        needs_multi = result.get("needs_multi_madhab", False)
                        reason = result.get("reason", "LLM analysis completed")
                        logger.info(
                            f"Orchestrator LLM analysis: needs_multi_madhab={needs_multi}, reason={reason}"
                        )
                        return (needs_multi, reason)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse extracted JSON: {json_match[:100]}")
                
                # Fallback: try to infer from response text
                response_lower = response_text.lower()
                if "true" in response_lower or '"needs_multi_madhab": true' in response_lower:
                    return (
                        True,
                        "LLM determined multi-madhab response is needed",
                    )
                else:
                    return (
                        False,
                        "LLM determined single response is sufficient",
                    )

        except Exception as e:
            logger.error(f"LLM classification failed: {e}, falling back to keyword check")
            # Fallback to keyword-based check if LLM fails
            return self._fallback_keyword_check(question)

    def _fallback_keyword_check(self, question: str) -> tuple[bool, str]:
        """
        Fallback keyword-based check if LLM classification fails.

        Args:
            question: User's question

        Returns:
            Tuple of (should_use_multi_madhab: bool, reason: str)
        """
        question_lower = question.lower()

        # Check if question explicitly asks for multiple madhabs
        multi_madhab_indicators = [
            "all madhabs",
            "all schools",
            "compare",
            "differences",
            "مقارنة",
            "الفرق",
            "جميع المذاهب",
            "كل المذاهب",
        ]

        if any(indicator in question_lower for indicator in multi_madhab_indicators):
            return (True, "User explicitly asked for comparison across madhabs")

        # Check if question is about general fiqh (not specific to one madhab)
        specific_madhab_indicators = [
            "maliki",
            "hanafi",
            "shafii",
            "hanbali",
            "مالكي",
            "حنفي",
            "شافعي",
            "حنبلي",
        ]

        if any(indicator in question_lower for indicator in specific_madhab_indicators):
            return (
                False,
                "Question is about a specific madhab, not multi-madhab comparison",
            )

        # Default: use multi-madhab for general fiqh questions
        return (True, "General fiqh question - provide multi-madhab perspective")


# Singleton instance
_orchestrator_instance: OrchestratorService | None = None


def get_orchestrator_service() -> OrchestratorService:
    """
    Get or create singleton orchestrator instance.

    Returns:
        OrchestratorService instance
    """
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = OrchestratorService()
    return _orchestrator_instance

