#!/usr/bin/env python3
"""
Direct Shamela Web Scraper for Maliki Fiqh Books

Scrapes book content directly from shamela.ws HTML pages,
bypassing the need for .bok archives or API authentication.

Based on the approach from web-scraping-maktabah-shamela reference.
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import time

import httpx
from bs4 import BeautifulSoup
from loguru import logger


class ShamelaDirectScraper:
    """Scrapes Shamela books directly from HTML pages."""

    def __init__(
        self,
        output_dir: str = "data/shamela/raw_text",
        delay: float = 2.0,
        max_pages_per_book: int = 3000,
    ) -> None:
        """
        Initialize scraper.

        Args:
            output_dir: Directory to save scraped content
            delay: Delay between requests (seconds)
            max_pages_per_book: Safety limit for page iteration
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.delay = delay
        self.max_pages_per_book = max_pages_per_book

        self.session_headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
        }

    async def scrape_page(
        self,
        client: httpx.AsyncClient,
        book_id: str,
        page_num: int,
    ) -> Optional[str]:
        """
        Scrape a single page from a Shamela book.

        Args:
            client: HTTP client
            book_id: Book identifier
            page_num: Page number

        Returns:
            Page text content or None if page doesn't exist
        """
        url = f"https://shamela.ws/book/{book_id}/{page_num}"

        try:
            response = await client.get(url, timeout=30.0)

            if response.status_code == 404:
                return None

            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Find wrapper container
            wrapper = soup.find(id="wrapper")
            if not wrapper:
                logger.warning(f"No wrapper found for {url}")
                return None

            # Extract text from nass divs
            nass_divs = wrapper.find_all("div", class_="nass")

            if not nass_divs:
                return None

            content_parts = []
            for nass_div in nass_divs:
                paragraphs = nass_div.find_all("p")
                for para in paragraphs:
                    text = para.get_text(strip=True)
                    if text:
                        content_parts.append(text)

            return "\n".join(content_parts) if content_parts else None

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return None
            logger.error(f"HTTP error for {url}: {exc}")
            return None
        except Exception as exc:
            logger.error(f"Failed to scrape {url}: {exc}")
            return None

    async def scrape_book(
        self,
        client: httpx.AsyncClient,
        book_id: str,
        book_title: str,
        author: str,
    ) -> Dict[str, Any]:
        """
        Scrape all pages from a Shamela book.

        Args:
            client: HTTP client
            book_id: Book identifier
            book_title: Book title
            author: Author name

        Returns:
            Book data with pages
        """
        logger.info(f"📖 Scraping book {book_id}: {book_title} by {author}")

        pages = []
        page_num = 1
        consecutive_empty = 0

        while page_num <= self.max_pages_per_book:
            content = await self.scrape_page(client, book_id, page_num)

            if content is None or len(content) < 50:
                consecutive_empty += 1
                # Stop if we hit 3 consecutive empty/missing pages
                if consecutive_empty >= 3:
                    logger.info(f"   Reached end at page {page_num - 3}")
                    break
            else:
                consecutive_empty = 0
                pages.append({
                    "page": page_num,
                    "content": content,
                })
                logger.debug(f"   ✅ Page {page_num}: {len(content)} chars")

            page_num += 1

            # Rate limiting
            await asyncio.sleep(self.delay)

        logger.info(f"   ✅ Scraped {len(pages)} pages from {book_title}")

        return {
            "book_id": book_id,
            "title": book_title,
            "author": author,
            "pages": pages,
            "total_pages": len(pages),
        }

    async def scrape_category(self, category_url: str = "https://shamela.ws/category/15") -> List[Dict[str, str]]:
        """
        Extract book list from category page.

        Args:
            category_url: Shamela category URL

        Returns:
            List of book metadata dictionaries
        """
        logger.info(f"📥 Fetching category listing from {category_url}")

        async with httpx.AsyncClient(headers=self.session_headers) as client:
            response = await client.get(category_url, timeout=30.0)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        books = []

        for item in soup.select("#cat_books .book_item"):
            title_tag = item.find("a", class_="book_title")
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            book_url = title_tag["href"]
            book_id = book_url.rstrip("/").split("/")[-1]

            author_tag = item.find("a", class_="text-gray")
            author = author_tag.get_text(strip=True) if author_tag else "Unknown"

            books.append({
                "book_id": book_id,
                "title": title,
                "author": author,
                "url": book_url,
            })

        logger.info(f"✅ Found {len(books)} Maliki fiqh books\n")
        return books

    async def scrape_all_books(
        self,
        books: List[Dict[str, str]],
        start_index: int = 0,
        max_books: Optional[int] = None,
    ) -> None:
        """
        Scrape multiple books and save to disk.

        Args:
            books: List of book metadata
            start_index: Index to start from (for resuming)
            max_books: Maximum number of books to scrape
        """
        async with httpx.AsyncClient(
            headers=self.session_headers,
            follow_redirects=True,
            timeout=30.0,
        ) as client:

            end_index = len(books) if max_books is None else min(start_index + max_books, len(books))

            for i, book_meta in enumerate(books[start_index:end_index], start=start_index + 1):
                try:
                    logger.info(f"\n[{i}/{end_index}] Processing: {book_meta['title']}")

                    # Scrape book
                    book_data = await self.scrape_book(
                        client,
                        book_meta["book_id"],
                        book_meta["title"],
                        book_meta["author"],
                    )

                    # Save to file
                    output_file = self.output_dir / f"{book_meta['book_id']}.json"
                    with output_file.open("w", encoding="utf-8") as f:
                        json.dump(book_data, f, ensure_ascii=False, indent=2)

                    logger.info(f"   💾 Saved to {output_file}\n")

                except Exception as exc:
                    logger.error(f"   ❌ Failed to scrape {book_meta['book_id']}: {exc}\n")
                    continue


async def main() -> None:
    """Main execution."""
    print("\n" + "=" * 70)
    print("🕌 SHAMELA MALIKI FIQH DIRECT SCRAPER")
    print("=" * 70 + "\n")

    scraper = ShamelaDirectScraper()

    # Step 1: Get book list
    books = await scraper.scrape_category()

    # Step 2: Scrape all books (or subset for testing)
    print(f"Starting scrape of {len(books)} books...")
    print("This will take several hours with rate limiting.\n")

    # For testing, scrape first 3 books; remove max_books for full scrape
    await scraper.scrape_all_books(books, start_index=0, max_books=3)

    print("\n" + "=" * 70)
    print("✨ SCRAPING COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Review scraped files in data/shamela/raw_text/")
    print("  2. Run: python scripts/shamela_converter_direct.py")
    print("  3. Run: python scrape_and_populate_rag.py")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())


