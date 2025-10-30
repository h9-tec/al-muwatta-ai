"""
Populate Qdrant with curated texts for all four madhabs.

Usage:
    python populate_all_madhabs.py

This script bootstraps the collections using curated content from the
per-madhab scrapers. Extend later with full scraping/ETL as needed.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable

from loguru import logger

from src.services.fiqh_rag_service import FiqhRAG
from src.services.multi_madhab_scraper import load_predefined_content, to_ingestion_stream


def ingest_documents(rag: FiqhRAG, documents: Iterable[Dict[str, Any]]) -> int:
    added = 0
    for doc in documents:
        try:
            ok = rag.add_document(text=doc["text"], metadata=doc["metadata"])
            if ok:
                added += 1
        except Exception as exc:
            logger.error(f"Failed to add doc: {exc}")
    return added


def main() -> None:
    logger.info("Loading curated multi-madhab content...")
    docs = load_predefined_content()
    stream = to_ingestion_stream(docs)

    rag = FiqhRAG()
    total = ingest_documents(rag, stream)
    stats = rag.get_statistics()

    logger.info(f"✅ Ingested {total} curated documents.")
    logger.info(f"Collections: {stats['collections']}")


if __name__ == "__main__":
    main()


