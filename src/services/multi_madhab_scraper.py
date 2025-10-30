"""
Multi-madhab content orchestrator.

Aggregates curated/predefined texts across Maliki, Hanafi, Shafi'i, and Hanbali
scrapers to bootstrap the knowledge base, and provides utilities to normalize
documents ready for ingestion into `FiqhRAG`.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Iterator, List

from loguru import logger

from .fiqh_scraper import MalikiFiqhScraper
from .hanafi_scraper import HanafiFiqhScraper
from .shafii_scraper import ShafiiFiqhScraper
from .hanbali_scraper import HanbaliFiqhScraper


def load_predefined_content() -> List[Dict[str, Any]]:
    """Load curated content across all four madhabs.

    Returns list of dicts with keys: text, topic, madhab, category, source, references.
    """
    all_docs: List[Dict[str, Any]] = []

    scrapers = [
        ("maliki", MalikiFiqhScraper(), "get_predefined_maliki_texts"),
        ("hanafi", HanafiFiqhScraper(), "get_predefined_texts"),
        ("shafii", ShafiiFiqhScraper(), "get_predefined_texts"),
        ("hanbali", HanbaliFiqhScraper(), "get_predefined_texts"),
    ]

    for key, scraper, method_name in scrapers:
        try:
            getter = getattr(scraper, method_name)
            docs = getter()  # type: ignore[call-arg]
            logger.info(f"Loaded {len(docs)} curated documents for {key}")
            all_docs.extend(docs)
        except Exception as exc:
            logger.warning(f"Failed to load curated docs for {key}: {exc}")

    return all_docs


def to_ingestion_stream(docs: Iterable[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
    """Normalize docs to ingestion items suitable for FiqhRAG.add_document()."""
    for d in docs:
        text = d.get("text", "").strip()
        if not text:
            continue
        yield {
            "text": text,
            "metadata": {
                "topic": d.get("topic", ""),
                "madhab": d.get("madhab", ""),
                "category": d.get("category", "general"),
                "source": d.get("source", "Fiqh Compilation"),
                "references": ",".join(d.get("references", [])),
            },
        }


