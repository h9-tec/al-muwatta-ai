#!/usr/bin/env python3
"""
Shamela JSON to RAG Chunks Converter

Transforms Shamela book JSON files into normalized chunks suitable for
Qdrant vector database ingestion.

Input: data/shamela/raw/*.json (from Node downloader)
Output: data/shamela/json/*.jsonl (chunked content with metadata)
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Iterator
from loguru import logger


class ShamelaConverter:
    """Converts Shamela book JSON to RAG-ready chunks."""

    def __init__(
        self,
        input_dir: str = "data/shamela/raw",
        output_dir: str = "data/shamela/json",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> None:
        """
        Initialize the converter.

        Args:
            input_dir: Directory containing Shamela JSON files
            output_dir: Directory for chunked output
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap between chunks for context preservation
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize Arabic text from Shamela.

        Args:
            text: Raw text from Shamela page

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        # Remove footnote markers [1], [2], etc.
        text = re.sub(r'\[\d+\]', '', text)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        # Remove page markers like ص12، ص:15
        text = re.sub(r'ص\s*:?\s*\d+', '', text)

        return text

    def _chunk_text(self, text: str, book_id: str, page_num: int) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks.

        Args:
            text: Full page text
            book_id: Book identifier
            page_num: Page number

        Returns:
            List of chunk dictionaries
        """
        if not text or len(text) < 50:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for Arabic sentence endings: . ? ! ؟ ۔
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
                    "start_char": start,
                    "end_char": end,
                })

            # Move to next chunk with overlap
            start = end - self.chunk_overlap if end < len(text) else end

        return chunks

    def _extract_book_metadata(self, book_data: Dict[str, Any], book_id: str) -> Dict[str, str]:
        """
        Extract metadata from Shamela book JSON.

        Args:
            book_data: Parsed book JSON
            book_id: Book identifier

        Returns:
            Metadata dictionary
        """
        # Shamela book structure: { pages: [...], titles: [...] }
        metadata = {
            "source": "Shamela",
            "book_id": book_id,
            "madhab": "Maliki",
            "category": "fiqh_maliki",
            "language": "Arabic",
        }

        # Try to extract title from first title entry
        if "titles" in book_data and book_data["titles"]:
            first_title = book_data["titles"][0]
            if "content" in first_title:
                metadata["book_title"] = self._clean_text(first_title["content"])

        return metadata

    def convert_book(self, json_path: Path) -> Iterator[Dict[str, Any]]:
        """
        Convert a single Shamela book JSON to chunks.

        Args:
            json_path: Path to Shamela book JSON file

        Yields:
            Chunk dictionaries with text and metadata
        """
        try:
            with json_path.open("r", encoding="utf-8") as f:
                book_data = json.load(f)

            book_id = json_path.stem  # Extract ID from filename
            base_metadata = self._extract_book_metadata(book_data, book_id)

            logger.info(f"Processing book {book_id}: {base_metadata.get('book_title', 'Unknown')}")

            pages = book_data.get("pages", [])
            total_chunks = 0

            for page in pages:
                page_content = page.get("content", "")
                page_num = page.get("page", page.get("id", 0))

                # Clean the content
                cleaned = self._clean_text(page_content)

                if not cleaned:
                    continue

                # Split into chunks
                page_chunks = self._chunk_text(cleaned, book_id, page_num)

                for chunk in page_chunks:
                    yield {
                        "text": chunk["text"],
                        "metadata": {
                            **base_metadata,
                            "page": chunk["page"],
                            "chunk_index": chunk["chunk_index"],
                        },
                    }
                    total_chunks += 1

            logger.info(f"✅ Extracted {total_chunks} chunks from {len(pages)} pages")

        except Exception as exc:
            logger.error(f"Failed to process {json_path}: {exc}")

    def convert_all(self) -> None:
        """Convert all Shamela JSON files in input directory."""
        json_files = list(self.input_dir.glob("*.json"))

        if not json_files:
            logger.warning(f"No JSON files found in {self.input_dir}")
            return

        logger.info(f"Found {len(json_files)} Shamela book files to process")

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
    print("📚 SHAMELA TO RAG CHUNKS CONVERTER")
    print("=" * 70 + "\n")

    converter = ShamelaConverter()
    converter.convert_all()

    print("\n" + "=" * 70)
    print("✨ Next step: python scrape_and_populate_rag.py")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()





