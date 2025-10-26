"""
Comprehensive Maliki Fiqh Web Scraper.

This scraper collects Maliki fiqh content from ALL available online sources.
"""

import json
from pathlib import Path
from typing import Generator, Dict, Any, Set
from urllib.parse import urljoin, urlparse

import scrapy
from bs4 import BeautifulSoup
from loguru import logger
import html2text
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.pipelines.files import FilesPipeline


def _has_arabic(text: str) -> bool:
    """Return True if the string contains Arabic characters."""
    for ch in text:
        if "\u0600" <= ch <= "\u06FF" or "\u0750" <= ch <= "\u077F" or "\u08A0" <= ch <= "\u08FF":
            return True
    return False


class _BaseContentSpider(scrapy.Spider):
    """Shared utilities for Maliki content spiders."""

    html_converter = html2text.HTML2Text()
    html_converter.ignore_links = False
    html_converter.ignore_images = True

    def _clean_html(self, html: str) -> Dict[str, str]:
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "noscript", "iframe"]):
            tag.decompose()
        text_plain = soup.get_text("\n", strip=True)
        markdown = self.html_converter.handle(str(soup))
        return {"text": text_plain, "markdown": markdown}


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
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS": 1,
    }

    def parse(self, response):
        """Parse category pages."""
        articles = response.css("article, .post")

        for article in articles:
            title = article.css("h2::text, h3::text, .title::text").get()
            link = article.css("a::attr(href)").get()

            if link:
                yield response.follow(link, callback=self.parse_article)

        next_page = response.css("a.next::attr(href), .pagination a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_article(self, response):
        """Parse individual article."""
        title = response.css("h1::text, .entry-title::text").get()
        content = response.css(".entry-content, article, .post-content").get()

        if content:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, "lxml")
            text = soup.get_text(separator="\n", strip=True)

            yield {
                "title": title.strip() if title else "Untitled",
                "text": text,
                "url": response.url,
                "source": "Maliki Fiqh QA",
                "madhab": "Maliki",
                "language": "English",
            }


class IslamQAMalikiSpider(scrapy.Spider):
    """Scrape IslamQA for Maliki-tagged content."""

    name = "islamqa_maliki"
    allowed_domains = ["islamqa.info"]
    start_urls = [
        "https://islamqa.info/en/categories/topics/105/maliki",
        "https://islamqa.info/ar/categories/topics/105/",
    ]

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 3,
        "CONCURRENT_REQUESTS": 1,
    }

    def parse(self, response):
        """Parse question listing."""
        questions = response.css(".question-listing-item, .qa-item")

        for q in questions:
            link = q.css("a::attr(href)").get()
            if link:
                yield response.follow(link, callback=self.parse_question)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_question(self, response):
        """Parse individual Q&A."""
        title = response.css("h1::text, .question-title::text").get()
        answer = response.css(".answer-text, .fatwa-text, article").get()

        if answer:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(answer, "lxml")
            text = soup.get_text(separator="\n", strip=True)

            yield {
                "title": title.strip() if title else "Q&A",
                "text": text,
                "url": response.url,
                "source": "IslamQA",
                "madhab": "Maliki",
                "language": "ar" if "/ar/" in response.url else "en",
            }


class AustralianLibrarySpider(scrapy.Spider):
    """Scrape Australian Islamic Library for Maliki books."""

    name = "australian_library"
    allowed_domains = ["australianislamiclibrary.org"]
    start_urls = [
        "https://www.australianislamiclibrary.org/maliki-fiqh---arabic-books.html",
    ]

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 2,
    }

    def parse(self, response):
        """Parse book listings."""
        books = response.css(".product-item, .book-item, a[href$='.pdf']")

        for book in books:
            title = book.css("::text").get()
            link = book.css("::attr(href)").get()

            if link and link.endswith(".pdf"):
                yield {
                    "title": title.strip() if title else "Maliki Book",
                    "pdf_url": response.urljoin(link),
                    "url": response.url,
                    "source": "Australian Islamic Library",
                    "madhab": "Maliki",
                    "language": "Arabic",
                    "type": "pdf",
                }


class MalikiFiqhSiteSpider(_BaseContentSpider):
    """Deep crawl of MalikiFiqhQA to capture all articles and resources."""

    name = "malikifiqh_full"
    allowed_domains = ["malikifiqhqa.com"]
    start_urls = ["https://malikifiqhqa.com/"]

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS": 1,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visited: Set[str] = set()
        self.article_selectors = ["article", ".entry-content", "#primary"]

    def parse(self, response):
        url = response.url.split("#")[0]
        if url in self.visited:
            return
        self.visited.add(url)

        if self._looks_like_article(response):
            yield from self._parse_article(response)

        for href in response.css("a::attr(href)").getall():
            next_url = urljoin(response.url, href.strip())
            if not self._should_follow(next_url):
                continue
            yield scrapy.Request(next_url, callback=self.parse)

    def _looks_like_article(self, response: scrapy.http.Response) -> bool:
        if response.css("article h1, article .entry-title, h1.entry-title"):
            return True
        if "category" in response.url or "202" in response.url:
            # Year/month permalinks include content
            return bool(response.css(".entry-content"))
        return False

    def _parse_article(self, response):
        title = response.css("h1.entry-title::text, h1::text").get()
        content_html = response.css(".entry-content, article").get()
        if not content_html:
            return

        meta = self._clean_html(content_html)
        plain_text = meta["text"]
        markdown = meta["markdown"]
        language = "Arabic" if _has_arabic(plain_text) else "English"
        tags = [t.strip() for t in response.css(".tag-links a::text, .cat-links a::text").getall() if t.strip()]
        yield {
            "title": title.strip() if title else "Maliki Fiqh Article",
            "text": plain_text,
            "markdown": markdown,
            "url": response.url,
            "tags": tags,
            "source": "Maliki Fiqh QA",
            "madhab": "Maliki",
            "language": language,
            "type": "article",
        }

    def _should_follow(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.netloc and parsed.netloc not in self.allowed_domains:
            return False
        if parsed.scheme not in {"http", "https"}:
            return False
        if any(url.lower().endswith(ext) for ext in [".jpg", ".png", ".gif", ".svg", ".zip", ".mp3"]):
            return False
        if "?share=" in url or "#respond" in url:
            return False
        if url in self.visited:
            return False
        return True


class ArqanMalikiBlogSpider(_BaseContentSpider):
    """Scrape Arqan Academy blog posts on Maliki fiqh."""

    name = "arqan_maliki_blog"
    allowed_domains = ["arqanacademy.com"]
    start_urls = ["https://arqanacademy.com/en/blogs/Maliki-Fiqh"]

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS": 1,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen: Set[str] = set()

    def parse(self, response):
        url = response.url.split("#")[0]
        if url in self.seen:
            return
        self.seen.add(url)

        yield from self._parse_article(response)

        for href in response.css("a::attr(href)").getall():
            next_url = urljoin(response.url, href.strip())
            if not self._should_follow(next_url):
                continue
            yield scrapy.Request(next_url, callback=self.parse)

    def _parse_article(self, response):
        content = response.css("article, .blog-details, .page-content").get()
        if not content:
            return

        title = response.css("h1::text, .blog-title::text").get() or "Maliki Fiqh Article"
        meta = self._clean_html(content)
        plain_text = meta["text"]
        markdown = meta["markdown"]
        tags = [tag.strip() for tag in response.css(".tagcloud a::text, .blog-tags a::text").getall() if tag.strip()]
        published = response.css("time::attr(datetime), .blog-date::text").get()
        yield {
            "title": title.strip(),
            "text": plain_text,
            "markdown": markdown,
            "url": response.url,
            "tags": tags,
            "source": "Arqan Academy",
            "madhab": "Maliki",
            "language": "Arabic" if _has_arabic(plain_text) else "English",
            "published": published.strip() if published else None,
            "type": "article",
        }

    def _should_follow(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.netloc and parsed.netloc not in self.allowed_domains:
            return False
        if parsed.scheme not in {"http", "https"}:
            return False
        if any(segment in parsed.path for segment in ["/courses", "/pricing", "/contact", "/about"]):
            return False
        if url in self.seen:
            return False
        return True


class SayfAlHaqqMalikiSpider(_BaseContentSpider):
    """Scrape Sayf al Haqq Maliki fiqh page and capture linked PDFs."""

    name = "sayf_al_haqq_maliki"
    allowed_domains = ["sayfalhaqq.wordpress.com", "wordpress.com"]
    start_urls = ["https://sayfalhaqq.wordpress.com/maliki-fiqh/"]

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS": 1,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visited: Set[str] = set()

    def parse(self, response):
        page_url = response.url.split("#")[0]
        if page_url in self.visited:
            return
        self.visited.add(page_url)

        content_type = response.headers.get(b"Content-Type", b"").decode().lower()
        if "application/pdf" in content_type:
            yield {
                "title": page_url.split("/")[-1],
                "pdf_url": page_url,
                "url": response.request.meta.get("referer", page_url),
                "source": "Sayf al Haqq",
                "madhab": "Maliki",
                "language": "Arabic" if "ar" in page_url else "English",
                "type": "pdf",
            }
            return

        # Extract content from the main Maliki fiqh page
        main_content = response.css("article, .entry-content, .post-content, #content").get()
        if main_content:
            meta = self._clean_html(main_content)
            language = "Arabic" if _has_arabic(meta["text"]) else "English"
            yield {
                "title": response.css("h1.entry-title::text, h1::text").get("Maliki Fiqh Resources").strip(),
                "text": meta["text"],
                "markdown": meta["markdown"],
                "url": response.url,
                "tags": ["Maliki Fiqh", "Resource Hub"],
                "source": "Sayf al Haqq",
                "madhab": "Maliki",
                "language": language,
                "type": "landing_page",
            }

        # Capture PDF links for downstream download
        for link in response.css("a::attr(href)").getall():
            href = link.strip()
            if not href:
                continue
            absolute = urljoin(response.url, href)
            if ".pdf" in absolute.lower():
                yield {
                    "title": absolute.split("/")[-1],
                    "pdf_url": absolute,
                    "url": response.url,
                    "source": "Sayf al Haqq",
                    "madhab": "Maliki",
                    "language": "Arabic" if "ar" in absolute.lower() else "English",
                    "type": "pdf",
                }

        # Follow internal links within the WordPress site for additional context pages
        for href in response.css("a::attr(href)").getall():
            next_url = urljoin(response.url, href.strip())
            if not self._should_follow(next_url):
                continue
            yield scrapy.Request(next_url, callback=self.parse)

    def _should_follow(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return False
        if parsed.netloc and parsed.netloc not in self.allowed_domains:
            return False
        if any(segment in parsed.path.lower() for segment in ["/comment", "wp-login", "feed", "tag", "category"]):
            return False
        if url in self.visited:
            return False
        return True


class IIUMLawbaseMalikiSpider(_BaseContentSpider):
    """Scrape IIUM Lawbase Maliki fiqh pages and linked resources."""

    name = "iium_maliki_lawbase"
    allowed_domains = ["www.iium.edu.my", "iium.edu.my"]
    start_urls = ["https://www.iium.edu.my/deed/lawbase/maliki_fiqh/index.html"]

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS": 1,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visited: Set[str] = set()

    def parse(self, response):
        clean_url = response.url.split("#")[0]
        if clean_url in self.visited:
            return
        self.visited.add(clean_url)

        content_type = response.headers.get(b"Content-Type", b"").decode().lower()
        if "application/pdf" in content_type:
            yield {
                "title": clean_url.split("/")[-1],
                "pdf_url": clean_url,
                "url": response.request.meta.get("referer", clean_url),
                "source": "IIUM Lawbase",
                "madhab": "Maliki",
                "language": "English",
                "type": "pdf",
            }
            return

        content = response.css("article, .entry-content, .post-content, #content, body").get()
        if content:
            meta = self._clean_html(content)
            language = "Arabic" if _has_arabic(meta["text"]) else "English"
            tags = [t.strip() for t in response.css(".breadcrumbs a::text, .category::text").getall() if t.strip()]
            yield {
                "title": response.css("h1::text, title::text").get("IIUM Maliki Fiqh").strip(),
                "text": meta["text"],
                "markdown": meta["markdown"],
                "url": response.url,
                "tags": tags or ["Maliki Fiqh"],
                "source": "IIUM Lawbase",
                "madhab": "Maliki",
                "language": language,
                "type": "article",
            }

        for href in response.css("a::attr(href)").getall():
            if not href:
                continue
            absolute = urljoin(response.url, href.strip())
            if ".pdf" in absolute.lower():
                yield {
                    "title": absolute.split("/")[-1],
                    "pdf_url": absolute,
                    "url": response.url,
                    "source": "IIUM Lawbase",
                    "madhab": "Maliki",
                    "language": "English",
                    "type": "pdf",
                }
                continue

            if not self._should_follow(absolute):
                continue
            yield scrapy.Request(absolute, callback=self.parse)

    def _should_follow(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return False
        if parsed.netloc and parsed.netloc not in self.allowed_domains:
            return False
        if "/maliki_fiqh" not in parsed.path:
            return False
        if any(segment in parsed.path.lower() for segment in ["/print", "?", "#"]):
            return False
        if url in self.visited:
            return False
        return True


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


def run_all_scrapers(output_file: str = "data/scraped_maliki_all.json"):
    """
    Run all Maliki fiqh scrapers.

    Args:
        output_file: Path to save scraped data
    """
    logger.info("🕷️  Starting comprehensive Maliki fiqh scraping...")

    process = CrawlerProcess({
        "USER_AGENT": "Mozilla/5.0 (compatible; IslamicEducationBot/1.0)",
        "ROBOTSTXT_OBEY": True,
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 2,
        "FEEDS": {
            output_file: {
                "format": "json",
                "encoding": "utf8",
                "overwrite": True,
            },
        },
    })

    process.crawl(MalikiFiqhQASpider)
    process.crawl(IslamQAMalikiSpider)
    process.crawl(AustralianLibrarySpider)
    process.crawl(MalikiFiqhSiteSpider)
    process.crawl(ArqanMalikiBlogSpider)
    process.crawl(SayfAlHaqqMalikiSpider)
    process.crawl(IIUMLawbaseMalikiSpider)

    process.start()
    logger.info(f"✅ Scraping completed! Data saved to {output_file}")


if __name__ == "__main__":
    run_all_scrapers()

