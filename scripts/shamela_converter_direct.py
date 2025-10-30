#!/usr/bin/env python3
"""
Shamela Direct JSON to RAG Chunks Converter

Transforms directly scraped Shamela book JSON files into normalized chunks
suitable for Qdrant vector database ingestion.

Input: data/shamela/raw_text/*.json (from direct scraper)
Output: data/shamela/json/shamela_maliki_chunks.jsonl (chunked content)
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Iterator
from loguru import logger


class ShamelaDirectConverter:
    """Converts directly scraped Shamela JSON to RAG-ready chunks."""

    def __init__(
        self,
        input_dir: str = "data/shamela/raw_text",
        output_dir: str = "data/shamela/json",
        chunk_size: int = 1200,
        chunk_overlap: int = 200,
    ) -> None:
        """
        Initialize the converter.

        Args:
            input_dir: Directory containing scraped Shamela JSON files
            output_dir: Directory for chunked output
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap between chunks
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _clean_text(self, text: str) -> str:
        """Clean Arabic text."""
        if not text:
            return ""

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        # Remove page markers
        text = re.sub(r'ص\s*:?\s*\d+', '', text)
        text = re.sub(r'\[\d+\]', '', text)

        return text

    def _chunk_text(self, text: str, book_id: str, page_num: int) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks."""
        if not text or len(text) < 100:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # Break at sentence boundary
            if end < len(text):
                last_period = max(
                    text.rfind('.', start, end),
                    text.rfind('؟', start, end),
                    text.rfind('۔', start, end),
                )
                if last_period > start + (self.chunk_size // 2):
                    end = last_period + 1

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "book_id": book_id,
                    "page": page_num,
                    "chunk_index": len(chunks),
                })

            start = end - self.chunk_overlap if end < len(text) else end

        return chunks

    def convert_book(self, json_path: Path) -> Iterator[Dict[str, Any]]:
        """
        Convert a single scraped book JSON to chunks.

        Args:
            json_path: Path to scraped book JSON

        Yields:
            Chunk dictionaries
        """
        try:
            with json_path.open("r", encoding="utf-8") as f:
                book_data = json.load(f)

            book_id = book_data.get("book_id", json_path.stem)
            book_title = book_data.get("title", "Unknown")
            author = book_data.get("author", "Unknown")

            logger.info(f"Processing: {book_title} ({book_id})")

            metadata = {
                "source": "Shamela",
                "book_id": book_id,
                "book_title": book_title,
                "author": author,
                "madhab": "Maliki",
                "category": "fiqh_maliki",
                "language": "Arabic",
            }

            pages = book_data.get("pages", [])
            total_chunks = 0

            for page_data in pages:
                page_num = page_data.get("page", 0)
                content = page_data.get("content", "")

                cleaned = self._clean_text(content)
                if not cleaned:
                    continue

                page_chunks = self._chunk_text(cleaned, book_id, page_num)

                for chunk in page_chunks:
                    yield {
                        "text": chunk["text"],
                        "metadata": {
                            **metadata,
                            "page": chunk["page"],
                            "chunk_index": chunk["chunk_index"],
                        },
                    }
                    total_chunks += 1

            logger.info(f"✅ Extracted {total_chunks} chunks from {len(pages)} pages")

        except Exception as exc:
            logger.error(f"Failed to process {json_path}: {exc}")

    def convert_all(self) -> None:
        """Convert all scraped Shamela JSON files."""
        json_files = list(self.input_dir.glob("*.json"))

        if not json_files:
            logger.warning(f"No JSON files found in {self.input_dir}")
            return

        logger.info(f"Found {len(json_files)} Shamela book files")

        output_file = self.output_dir / "shamela_maliki_chunks.jsonl"

        total_chunks = 0
        total_books = 0

        with output_file.open("w", encoding="utf-8") as out:
            for json_path in json_files:
                book_chunks = 0
                for chunk_data in self.convert_book(json_path):
                    out.write(json.dumps(chunk_data, ensure_ascii=False) + "\n")
                    book_chunks += 1
                    total_chunks += 1

                if book_chunks > 0:
                    total_books += 1

        logger.info(
            f"\n✅ Conversion complete: {total_chunks} chunks from {total_books} books"
        )
        logger.info(f"📄 Output: {output_file}")


def main() -> None:
    """Main execution."""
    print("\n" + "=" * 70)
    print("📚 SHAMELA DIRECT SCRAPER TO RAG CHUNKS CONVERTER")
    print("=" * 70 + "\n")

    converter = ShamelaDirectConverter()
    converter.convert_all()

    print("\n" + "=" * 70)
    print("✨ Next step: python scrape_and_populate_rag.py")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()





