"""
Scrapy Spider for Maliki Fiqh Resources.

This spider scrapes authentic Maliki fiqh texts from various trusted sources.
"""

import scrapy
from scrapy.http import Response
from typing import Generator, Dict, Any
import json
from pathlib import Path


class MalikiFiqhSpider(scrapy.Spider):
    """Spider for scraping Maliki fiqh books and articles."""

    name = "maliki_fiqh"
    allowed_domains = [
        "malikifiqhqa.com",
        "australianislamiclibrary.org",
        "sunnah.com",
        "islamqa.info",
    ]

    # Start URLs for Maliki content
    start_urls = [
        # Maliki Fiqh QA - English resources
        "https://malikifiqhqa.com/media__trashed/e-books/english/",
        
        # Australian Islamic Library - Arabic books
        "https://www.australianislamiclibrary.org/maliki-fiqh---arabic-books.html",
        
        # IslamQA Maliki tag
        "https://islamqa.info/en/categories/topics/105",
    ]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (compatible; IslamicEducationBot/1.0; +http://example.com/bot)',
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 1,  # Be polite
        'DOWNLOAD_DELAY': 2,  # 2 seconds delay
        'FEEDS': {
            'data/maliki_fiqh_raw.json': {
                'format': 'json',
                'encoding': 'utf8',
                'store_empty': False,
                'overwrite': True,
            },
        },
    }

    def parse(self, response: Response) -> Generator[Dict[str, Any], None, None]:
        """
        Parse main listing pages.

        Args:
            response: Scrapy response object

        Yields:
            Scraped items or follow-up requests
        """
        self.logger.info(f"Parsing: {response.url}")

        # Extract links to individual books/articles
        if "malikifiqhqa.com" in response.url:
            yield from self.parse_malikifiqhqa(response)
        elif "australianislamiclibrary.org" in response.url:
            yield from self.parse_australian_library(response)
        elif "islamqa.info" in response.url:
            yield from self.parse_islamqa(response)

    def parse_malikifiqhqa(self, response: Response) -> Generator[Dict[str, Any], None, None]:
        """Parse malikifiqhqa.com resources."""
        # Find PDF links or book content
        pdf_links = response.css('a[href$=".pdf"]::attr(href)').getall()

        for pdf_url in pdf_links:
            full_url = response.urljoin(pdf_url)
            yield scrapy.Request(
                url=full_url,
                callback=self.parse_pdf_link,
                meta={'source': 'Maliki Fiqh QA', 'url': full_url}
            )

        # Find article links
        article_links = response.css('article a::attr(href)').getall()
        for article_url in article_links:
            full_url = response.urljoin(article_url)
            yield scrapy.Request(
                url=full_url,
                callback=self.parse_article,
                meta={'source': 'Maliki Fiqh QA'}
            )

    def parse_australian_library(self, response: Response) -> Generator[Dict[str, Any], None, None]:
        """Parse Australian Islamic Library."""
        # Extract book information
        book_items = response.css('.product-item, .book-item')

        for book in book_items:
            title = book.css('.title::text, h3::text').get()
            description = book.css('.description::text, p::text').get()
            link = book.css('a::attr(href)').get()

            if title:
                yield {
                    'title': title.strip(),
                    'description': description.strip() if description else '',
                    'url': response.urljoin(link) if link else response.url,
                    'source': 'Australian Islamic Library',
                    'madhab': 'Maliki',
                    'language': 'Arabic',
                    'type': 'book',
                }

    def parse_islamqa(self, response: Response) -> Generator[Dict[str, Any], None, None]:
        """Parse IslamQA articles on Maliki topics."""
        # Extract question/answer pairs
        questions = response.css('.question-item, .qa-item')

        for qa in questions:
            title = qa.css('h2::text, .question-title::text').get()
            answer = qa.css('.answer-text::text, .fatwa-text::text').getall()
            link = qa.css('a::attr(href)').get()

            if title and answer:
                yield {
                    'title': title.strip(),
                    'text': ' '.join(answer).strip(),
                    'url': response.urljoin(link) if link else response.url,
                    'source': 'IslamQA',
                    'madhab': 'Maliki',
                    'type': 'qa',
                }

        # Follow pagination
        next_page = response.css('a.next::attr(href), .pagination a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_islamqa)

    def parse_pdf_link(self, response: Response) -> Dict[str, Any]:
        """Store PDF link for later processing."""
        return {
            'title': response.meta.get('title', 'Maliki Fiqh PDF'),
            'url': response.url,
            'source': response.meta.get('source', 'Unknown'),
            'madhab': 'Maliki',
            'type': 'pdf',
            'file_size': len(response.body),
        }

    def parse_article(self, response: Response) -> Dict[str, Any]:
        """Parse article/book page content."""
        title = response.css('h1::text, .title::text').get()
        content_paragraphs = response.css('article p::text, .content p::text').getall()
        content = '\n\n'.join(content_paragraphs)

        return {
            'title': title.strip() if title else 'Untitled',
            'text': content.strip(),
            'url': response.url,
            'source': response.meta.get('source', 'Unknown'),
            'madhab': 'Maliki',
            'type': 'article',
        }


class SimpleMalikiScraper:
    """Simple non-Scrapy scraper for direct URL content extraction."""

    DIRECT_SOURCES = [
        {
            "name": "Al-Risala",
            "url": "https://ia802800.us.archive.org/35/items/Risalah_201406/Risalah.pdf",
            "type": "pdf",
            "author": "Ibn Abi Zayd al-Qayrawani",
        },
        {
            "name": "Mukhtasar Khalil",
            "url": "https://archive.org/details/mukhtasar-khalil",
            "type": "web",
            "author": "Khalil ibn Ishaq",
        },
    ]

    @staticmethod
    def get_sources() -> list:
        """Get list of direct sources for download."""
        return SimpleMalikiScraper.DIRECT_SOURCES

