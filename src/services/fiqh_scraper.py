"""
Maliki Fiqh Web Scraper.

This module scrapes authentic Maliki fiqh resources from trusted sources.
"""

from typing import List, Dict, Any, Optional
import asyncio
import json
from pathlib import Path
import httpx
from bs4 import BeautifulSoup
import html2text
from loguru import logger
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

try:
    from scrapers.comprehensive_maliki_scraper import (
        SayfAlHaqqMalikiSpider,
        IIUMLawbaseMalikiSpider,
    )
except ModuleNotFoundError:  # pragma: no cover
    import sys
    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[2]
    if str(ROOT) not in sys.path:
        sys.path.append(str(ROOT))
    from scrapers.comprehensive_maliki_scraper import (  # type: ignore
        SayfAlHaqqMalikiSpider,
        IIUMLawbaseMalikiSpider,
    )


DATA_DIR = Path("data")
SAYF_JSONL = DATA_DIR / "sayf_al_haqq.jsonl"
IIUM_JSONL = DATA_DIR / "iium_maliki_lawbase.jsonl"
PDF_DIR = DATA_DIR / "pdf"

PDF_DIR.mkdir(exist_ok=True)


class MalikiFiqhScraper:
    """Scraper for Maliki fiqh texts from various sources."""

    # Key Maliki fiqh resources
    SOURCES = {
        "al_muwatta": {
            "name": "Al-Muwatta - Imam Malik",
            "url": "https://sunnah.com/malik",
            "description": "The foundational Hadith collection by Imam Malik",
        },
        "al_risala": {
            "name": "Al-Risala - Ibn Abi Zayd al-Qayrawani",
            "url": "https://www.islamicstudies.info/maaliki/risala/",
            "description": "Concise manual of Maliki fiqh",
        },
        "bidayat_mujtahid": {
            "name": "Bidayat al-Mujtahid - Ibn Rushd",
            "url": "https://archive.org/details/bidayat-al-mujtahid",
            "description": "Comparative fiqh including Maliki positions",
        },
    }

    def __init__(self) -> None:
        """Initialize the scraper."""
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True

    async def scrape_islamqa_maliki(
        self,
        query: str = "maliki",
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Scrape Maliki fiqh Q&A from IslamQA and similar sources.

        Args:
            query: Search query
            limit: Maximum number of articles to fetch

        Returns:
            List of fiqh articles with text and metadata
        """
        articles = []

        # Sample Maliki fiqh topics to scrape
        maliki_topics = [
            "maliki prayer rulings",
            "maliki fasting rules",
            "maliki zakat",
            "maliki hajj",
            "maliki purification wudu",
            "maliki marriage nikah",
            "maliki divorce talaq",
            "maliki inheritance",
            "maliki business transactions",
            "maliki food halal",
        ]

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                for topic in maliki_topics[:limit]:
                    logger.info(f"Fetching content for: {topic}")

                    # Note: This is a template - actual scraping would need
                    # to respect robots.txt and terms of service
                    article = {
                        "topic": topic,
                        "madhab": "Maliki",
                        "text": f"[Placeholder for {topic} content]",
                        "source": "to_be_scraped",
                        "url": "",
                    }

                    articles.append(article)
                    await asyncio.sleep(1)  # Rate limiting

        except Exception as e:
            logger.error(f"Error scraping Maliki fiqh: {e}")

        return articles

    async def scrape_custom_url(
        self,
        url: str,
        extract_selector: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Scrape content from a custom URL.

        Args:
            url: URL to scrape
            extract_selector: CSS selector for main content

        Returns:
            Scraped content with metadata
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'lxml')

                # Extract main content
                if extract_selector:
                    content_elem = soup.select_one(extract_selector)
                    content = content_elem.get_text() if content_elem else soup.get_text()
                else:
                    content = soup.get_text()

                # Convert to markdown
                markdown_text = self.html_converter.handle(response.text)

                return {
                    "url": url,
                    "title": soup.title.string if soup.title else "",
                    "text": content.strip(),
                    "markdown": markdown_text,
                    "word_count": len(content.split()),
                }

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None

    async def run_sayf_al_haqq_scraper(self) -> List[Dict[str, Any]]:
        """Run Scrapy spider to collect Sayf al Haqq Maliki resources."""
        loop = asyncio.get_running_loop()

        def _crawl() -> List[Dict[str, Any]]:
            items: List[Dict[str, Any]] = []

            settings = {
                "LOG_ENABLED": False,
                "USER_AGENT": "Mozilla/5.0 (compatible; MalikiFiqhBot/1.0)",
                "ITEM_PIPELINES": {},
                "FEEDS": {
                    str(SAYF_JSONL): {
                        "format": "jsonlines",
                        "overwrite": True,
                        "encoding": "utf8",
                    }
                },
            }

            process = CrawlerProcess(settings)

            process.crawl(SayfAlHaqqMalikiSpider)
            process.start()
            return items

        return await loop.run_in_executor(None, _crawl)

    async def run_iium_lawbase_scraper(self) -> List[Dict[str, Any]]:
        """Run Scrapy spider to harvest IIUM Lawbase Maliki fiqh content."""
        loop = asyncio.get_running_loop()

        def _crawl() -> List[Dict[str, Any]]:
            items: List[Dict[str, Any]] = []

            settings = {
                "LOG_ENABLED": False,
                "USER_AGENT": "Mozilla/5.0 (compatible; MalikiFiqhBot/1.0)",
                "ITEM_PIPELINES": {},
                "FEEDS": {
                    str(IIUM_JSONL): {
                        "format": "jsonlines",
                        "overwrite": True,
                        "encoding": "utf8",
                    }
                },
            }

            process = CrawlerProcess(settings)

            process.crawl(IIUMLawbaseMalikiSpider)
            process.start()
            return items

        return await loop.run_in_executor(None, _crawl)

    def get_predefined_maliki_texts(self) -> List[Dict[str, Any]]:
        """
        Get predefined Maliki fiqh texts for immediate use.

        Returns:
            List of foundational Maliki texts
        """
        return [
            {
                "id": "maliki_pillars_1",
                "topic": "The Five Pillars in Maliki Fiqh",
                "madhab": "Maliki",
                "category": "ibadah",
                "text": """
# The Five Pillars of Islam in Maliki Fiqh

## 1. Shahada (Declaration of Faith)
In the Maliki madhab, the Shahada must be pronounced correctly with understanding of its meaning.
The two testimonies are: "Ashhadu an la ilaha illa Allah, wa ashhadu anna Muhammadan rasul Allah"

## 2. Salah (Prayer)
- Five daily prayers are obligatory
- Maliki school has specific rulings on qunut, isti'adhah, and hand placement
- Jumu'ah (Friday prayer) is obligatory for male Muslims

## 3. Zakat (Obligatory Charity)
- Nisab (minimum threshold) must be met
- 2.5% on savings held for one lunar year
- Specific rules for agricultural products and livestock

## 4. Sawm (Fasting)
- Fasting during Ramadan is obligatory
- Maliki view on what breaks the fast
- Rules for making up missed fasts

## 5. Hajj (Pilgrimage)
- Obligatory once in a lifetime if able
- Specific Maliki rulings on Hajj rituals
- Conditions of obligation
                """,
                "source": "Maliki Fiqh Compilation",
                "references": ["Al-Risala", "Al-Muwatta"],
            },
            {
                "id": "maliki_wudu_1",
                "topic": "Wudu (Ablution) in Maliki Fiqh",
                "madhab": "Maliki",
                "category": "taharah",
                "text": """
# Wudu in Maliki Fiqh

## Obligations (Fard)
1. Intention (niyyah)
2. Washing the face
3. Washing the arms to the elbows
4. Wiping the entire head
5. Washing the feet to the ankles
6. Continuity (muwalah) - performing actions in succession
7. Order (tartib) - performing actions in the prescribed order

## Sunnan (Recommended Acts)
- Using siwak (tooth stick)
- Washing hands three times
- Rinsing mouth (madmadah)
- Sniffing water into nose (istinshaq)

## What Nullifies Wudu
- Natural discharge (urine, stool, gas)
- Deep sleep
- Loss of consciousness
- Touching private parts (in Maliki view, direct skin contact)
- Maliki specific: Eating camel meat does NOT break wudu

## Unique Maliki Positions
- Touching one's spouse does not break wudu
- Bleeding does not break wudu
- Vomiting does not break wudu
                """,
                "source": "Maliki Fiqh Compilation",
                "references": ["Al-Risala", "Mukhtasar Khalil"],
            },
            {
                "id": "maliki_prayer_1",
                "topic": "Prayer (Salah) Specific Rulings in Maliki Madhab",
                "madhab": "Maliki",
                "category": "salah",
                "text": """
# Prayer in Maliki Fiqh

## Hand Placement
- Arms are placed at the sides (not folded on chest)
- This is a distinctive feature of Maliki prayer

## Opening Takbir
- Raise hands to shoulder level
- Only raise hands for opening takbir (not in ruku or sujud)

## Recitation
- Basmala is not recited aloud before Al-Fatiha
- Imam recites loudly in Maghrib, Isha, and Fajr
- Silent in Dhuhr and Asr

## Qunut
- Not performed in Fajr prayer regularly
- Only done during calamities (Qunut al-Nawazil)

## Prostration of Forgetfulness (Sujud al-Sahw)
- Performed AFTER salam if one adds to prayer
- Performed BEFORE salam if one omits from prayer

## Maliki Position on Issues
- Following the Imam's movement immediately is required
- Witr is sunna muakkadah (confirmed sunnah), not wajib
- Combining prayers only allowed when traveling

## Invalidators
- Deliberate speech
- Excessive movement
- Eating or drinking
- Breaking wudu
                """,
                "source": "Maliki Fiqh Compilation",
                "references": ["Al-Risala", "Al-Mudawwana"],
            },
            {
                "id": "maliki_zakat_1",
                "topic": "Zakat in Maliki Madhab",
                "madhab": "Maliki",
                "category": "zakat",
                "text": """
# Zakat in Maliki Fiqh

## Conditions for Zakat on Wealth
1. Full ownership (milk tam)
2. Nisab reached (minimum threshold)
3. One lunar year passed (hawl)
4. Wealth is productive or intended for productivity
5. Free from debt

## Nisab Amounts
- Gold: 85 grams
- Silver: 595 grams
- Cash/Savings: Equivalent to gold or silver value
- Rate: 2.5% (1/40)

## Zakat on Agricultural Products
- Irrigated crops: 5% (1/20)
- Rain-fed crops: 10% (1/10)
- No hawl requirement - due at harvest

## Zakat on Livestock
Specific nisab for camels, cattle, sheep/goats as detailed in hadith

## Recipients (Masarif al-Zakat)
Eight categories mentioned in Quran 9:60:
1. The poor (fuqara)
2. The needy (masakin)
3. Zakat administrators
4. Those whose hearts are to be reconciled
5. Freeing slaves
6. Those in debt
7. In the path of Allah
8. Travelers in need

## Maliki Specific Rulings
- Jewelry worn by women: Maliki position is that it is NOT zakatable
- Zakat can be given to relatives (except direct dependents)
- Must be distributed in the same locality
                """,
                "source": "Maliki Fiqh Compilation",
                "references": ["Al-Risala", "Al-Muwatta"],
            },
            {
                "id": "maliki_fasting_1",
                "topic": "Fasting (Sawm) in Maliki Madhab",
                "madhab": "Maliki",
                "category": "sawm",
                "text": """
# Fasting in Maliki Fiqh

## Obligations of Ramadan Fasting
1. Intention (niyyah) - must be made each night before Fajr
2. Abstaining from food, drink, and sexual relations
3. From true dawn (Fajr) to sunset (Maghrib)

## What Breaks the Fast
- Deliberate eating or drinking
- Sexual intercourse
- Intentional vomiting
- Menstruation or post-natal bleeding
- Apostasy

## What Does NOT Break the Fast (Maliki View)
- Unintentional eating/drinking
- Swallowing saliva
- Using miswak/siwak
- Eye drops, ear drops
- Injection (non-nutritional)
- Tasting food (if not swallowed)

## Making Up Missed Fasts (Qada)
- Must be made up before next Ramadan
- Can be done non-consecutively
- Fidyah (feeding poor) for elderly who cannot fast

## Maliki Position on Kaffara (Expiation)
For intentional intercourse during Ramadan:
1. Free a slave (no longer applicable)
2. Fast 60 consecutive days
3. Feed 60 poor people

Order must be followed - cannot skip to feeding without trying fasting first.

## I'tikaf (Spiritual Retreat)
- Minimum duration: No specific minimum in Maliki madhab
- Must be in a mosque
- Recommended in last 10 days of Ramadan
                """,
                "source": "Maliki Fiqh Compilation",
                "references": ["Al-Risala", "Mukhtasar Khalil"],
            },
        ]

