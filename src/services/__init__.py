"""Business logic services for Nur Al-Ilm.

This package lazily exposes service classes to avoid heavy optional
dependencies at import time (e.g., qdrant_client, transformers).
"""

from typing import Any

__all__ = [
    "GeminiService",
    "MalikiFiqhRAG",
    "MalikiFiqhScraper",
    "MultiLLMService",
    "FiqhRAG",
    "get_fiqh_rag",
]


def __getattr__(name: str) -> Any:
    if name == "GeminiService":
        from .gemini_service import GeminiService
        return GeminiService
    if name == "MalikiFiqhRAG":
        from .rag_service import MalikiFiqhRAG
        return MalikiFiqhRAG
    if name == "MalikiFiqhScraper":
        from .fiqh_scraper import MalikiFiqhScraper
        return MalikiFiqhScraper
    if name == "MultiLLMService":
        from .multi_llm_service import MultiLLMService
        return MultiLLMService
    if name == "FiqhRAG":
        from .fiqh_rag_service import FiqhRAG
        return FiqhRAG
    if name == "get_fiqh_rag":
        from .fiqh_rag_service import get_fiqh_rag
        return get_fiqh_rag
    raise AttributeError(name)

