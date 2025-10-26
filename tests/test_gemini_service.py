"""
Comprehensive tests for Gemini AI Service.

This module tests the GeminiService integration with Google's Gemini API.
"""

import pytest
from src.services import GeminiService


class TestGeminiService:
    """Test suite for GeminiService."""

    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """Test that the Gemini service initializes correctly."""
        service = GeminiService()
        assert service is not None
        assert service.model is not None

    @pytest.mark.asyncio
    async def test_generate_content(self):
        """Test basic content generation."""
        service = GeminiService()

        content = await service.generate_content(
            "Explain the importance of Salah in one sentence."
        )

        assert content is not None
        assert isinstance(content, str)
        assert len(content) > 0

    @pytest.mark.asyncio
    async def test_explain_hadith(self):
        """Test Hadith explanation generation."""
        service = GeminiService()

        hadith = "إنما الأعمال بالنيات"  # Actions are by intentions

        explanation = await service.explain_hadith(hadith, language="english")

        assert explanation is not None
        assert isinstance(explanation, str)
        assert len(explanation) > 50

    @pytest.mark.asyncio
    async def test_answer_islamic_question(self):
        """Test answering Islamic questions."""
        service = GeminiService()

        question = "What are the five pillars of Islam?"

        answer = await service.answer_islamic_question(question, language="english")

        assert answer is not None
        assert isinstance(answer, str)
        # Should mention core pillars
        assert any(
            keyword in answer.lower()
            for keyword in ["shahada", "salah", "zakat", "sawm", "hajj"]
        )

    @pytest.mark.asyncio
    async def test_generate_daily_reminder(self):
        """Test generating daily Islamic reminders."""
        service = GeminiService()

        reminder = await service.generate_daily_reminder(
            theme="gratitude",
            language="english",
        )

        assert reminder is not None
        assert isinstance(reminder, str)
        assert len(reminder) > 0

    @pytest.mark.asyncio
    async def test_translate_with_context(self):
        """Test contextual translation."""
        service = GeminiService()

        text = "الحمد لله"

        translation = await service.translate_with_context(
            text,
            source_lang="arabic",
            target_lang="english",
        )

        assert translation is not None
        assert isinstance(translation, str)
        assert len(translation) > 0

