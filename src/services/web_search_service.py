"""
Web Search Service using Firecrawl.

This service enriches answers by scraping authoritative Islamic resources
via Firecrawl's /scrape endpoint.

Reference: https://docs.firecrawl.dev/features/scrape
"""

from __future__ import annotations

from typing import Any, Iterable

import httpx
from loguru import logger

from ..config import settings


FIRECRAWL_API_BASE = "https://api.firecrawl.dev/v2"


class WebSearchService:
    """Lightweight client for Firecrawl-powered scraping."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or settings.firecrawl_api_key or ""
        if not self.api_key:
            logger.warning("Firecrawl API key not configured; web search disabled")

    async def scrape_url(self, url: str, formats: list[str] | None = None) -> dict[str, Any]:
        """
        Scrape a single URL and return data payload with markdown/html.

        Returns empty dict if API key missing or request fails.
        """
        if not self.api_key:
            return {}

        try:
            payload: dict[str, Any] = {"url": url, "formats": formats or ["markdown"]}
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{FIRECRAWL_API_BASE}/scrape",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
                if isinstance(data, dict) and data.get("success") and isinstance(
                    data.get("data"), dict
                ):
                    return data["data"]
                return {}
        except Exception as exc:
            logger.error(f"Firecrawl scrape failed for {url}: {exc}")
            return {}

    async def scrape_urls(self, urls: Iterable[str], limit: int = 4) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for idx, url in enumerate(urls):
            if idx >= limit:
                break
            data = await self.scrape_url(url)
            if data:
                results.append({"url": url, **data})
        return results

    async def search(self, query: str, max_results: int = 5) -> list[str]:
        """Use Firecrawl search to get a wide set of URLs for a query.

        Falls back to returning an empty list if search is unavailable.
        """
        if not self.api_key:
            return []
        try:
            payload: dict[str, Any] = {"query": query, "limit": max_results}
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{FIRECRAWL_API_BASE}/search",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
                urls: list[str] = []
                # Try common shapes
                if isinstance(data, dict):
                    d = data.get("data") if isinstance(data.get("data"), dict) else data
                    # results: [{url:...}]
                    for item in d.get("results", []) if isinstance(d.get("results"), list) else []:
                        u = item.get("url")
                        if isinstance(u, str):
                            urls.append(u)
                    # links: [str]
                    for u in d.get("links", []) if isinstance(d.get("links"), list) else []:
                        if isinstance(u, str):
                            urls.append(u)
                return urls[:max_results]
        except Exception as exc:
            logger.error(f"Firecrawl search failed: {exc}")
            return []

    def build_source_urls(self, query: str) -> list[str]:
        """
        Build a conservative set of query URLs on reputable sites.
        We avoid scraping generic search engines; instead use site search endpoints.
        """
        q = query.replace(" ", "+")
        return [
            f"https://islamqa.info/en/search?keyword={q}",
            f"https://seekersguidance.org/?s={q}",
            f"https://sunnah.com/search?q={q}",
            f"https://islamweb.net/en/search?query={q}",
        ]


