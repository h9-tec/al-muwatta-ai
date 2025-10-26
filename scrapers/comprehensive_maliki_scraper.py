"""
Comprehensive Maliki Fiqh Web Scraper.

This scraper collects Maliki fiqh content from ALL available online sources.
"""

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import json
from pathlib import Path
from typing import Generator, Dict, Any
from loguru import logger


class MalikiFiqhQASpider(scrapy.Spider):
    """Scrape malikifiqhqa.com for English Maliki content."""

    name = "malikifiqhqa"
    allowed_domains = ["malikifiqhqa.com"]
    start_urls = [
        "https://malikifiqhqa.com/category/fiqh/",
        "https://malikifiqhqa.com/category/aqeedah/",
        "https://malikifiqhqa.com/category/general/",
    ]

    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 1,
    }

    def parse(self, response):
        """Parse category pages."""
        # Find article links
        articles = response.css('article, .post')
        
        for article in articles:
            title = article.css('h2::text, h3::text, .title::text').get()
            link = article.css('a::attr(href)').get()
            
            if link:
                yield response.follow(link, callback=self.parse_article)
        
        # Follow pagination
        next_page = response.css('a.next::attr(href), .pagination a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_article(self, response):
        """Parse individual article."""
        title = response.css('h1::text, .entry-title::text').get()
        content = response.css('.entry-content, article, .post-content').get()
        
        # Extract clean text
        if content:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'lxml')
            text = soup.get_text(separator='\n', strip=True)
            
            yield {
                'title': title.strip() if title else 'Untitled',
                'text': text,
                'url': response.url,
                'source': 'Maliki Fiqh QA',
                'madhab': 'Maliki',
                'language': 'English',
            }


class IslamQAMalikiSpider(scrapy.Spider):
    """Scrape IslamQA for Maliki-tagged content."""

    name = "islamqa_maliki"
    allowed_domains = ["islamqa.info"]
    start_urls = [
        "https://islamqa.info/en/categories/topics/105/maliki",  # Maliki tag
        "https://islamqa.info/ar/categories/topics/105/",  # Arabic
    ]

    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS': 1,
    }

    def parse(self, response):
        """Parse question listing."""
        questions = response.css('.question-listing-item, .qa-item')
        
        for q in questions:
            link = q.css('a::attr(href)').get()
            if link:
                yield response.follow(link, callback=self.parse_question)
        
        # Pagination
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_question(self, response):
        """Parse individual Q&A."""
        title = response.css('h1::text, .question-title::text').get()
        answer = response.css('.answer-text, .fatwa-text, article').get()
        
        if answer:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(answer, 'lxml')
            text = soup.get_text(separator='\n', strip=True)
            
            yield {
                'title': title.strip() if title else 'Q&A',
                'text': text,
                'url': response.url,
                'source': 'IslamQA',
                'madhab': 'Maliki',
                'language': 'ar' if '/ar/' in response.url else 'en',
            }


class AustralianLibrarySpider(scrapy.Spider):
    """Scrape Australian Islamic Library for Maliki books."""

    name = "australian_library"
    allowed_domains = ["australianislamiclibrary.org"]
    start_urls = [
        "https://www.australianislamiclibrary.org/maliki-fiqh---arabic-books.html",
    ]

    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 2,
    }

    def parse(self, response):
        """Parse book listings."""
        books = response.css('.product-item, .book-item, a[href*=".pdf"]')
        
        for book in books:
            title = book.css('::text').get()
            link = book.css('::attr(href)').get()
            
            if link and link.endswith('.pdf'):
                yield {
                    'title': title.strip() if title else 'Maliki Book',
                    'pdf_url': response.urljoin(link),
                    'url': response.url,
                    'source': 'Australian Islamic Library',
                    'madhab': 'Maliki',
                    'language': 'Arabic',
                    'type': 'pdf',
                }


def run_all_scrapers(output_file: str = "data/scraped_maliki_all.json"):
    """
    Run all Maliki fiqh scrapers.

    Args:
        output_file: Path to save scraped data
    """
    logger.info("🕷️  Starting comprehensive Maliki fiqh scraping...")

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (compatible; IslamicEducationBot/1.0)',
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
        'FEEDS': {
            output_file: {
                'format': 'json',
                'encoding': 'utf8',
                'overwrite': True,
            },
        },
    })

    # Add all spiders
    process.crawl(MalikiFiqhQASpider)
    process.crawl(IslamQAMalikiSpider)
    process.crawl(AustralianLibrarySpider)

    # Start crawling
    process.start()
    logger.info(f"✅ Scraping completed! Data saved to {output_file}")


if __name__ == "__main__":
    run_all_scrapers()

