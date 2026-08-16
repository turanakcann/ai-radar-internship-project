"""
connectors/crawl4ai_connector.py — Crawl4AI / Playwright fallback connector.

Used when a target source requires JavaScript rendering (e.g., SPA-based
blog platforms, Hugging Face Papers, Papers With Code).

This connector is NOT enabled by default in the Scout Agent.
To enable: import and add to scout_agent.py's asyncio.gather() call.

Architecture note:
  - Uses Crawl4AI for JS-rendered content extraction
  - Falls back to raw httpx if Crawl4AI is not installed
  - Returns same ScoutOutput schema as all other connectors
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Optional

import structlog

from core.schemas import ScoutOutput, SourceName

logger = structlog.get_logger(__name__)

# JS-rendered sources that need Playwright/Crawl4AI
JS_SOURCES = [
    {
        "name": "huggingface_papers",
        "url": "https://huggingface.co/papers",
        "source_name": SourceName.ARXIV,  # HF papers are arXiv papers
    },
    {
        "name": "paperswithcode",
        "url": "https://paperswithcode.com/latest",
        "source_name": SourceName.ARXIV,
    },
]


async def _try_crawl4ai(url: str) -> Optional[str]:
    """
    Attempt to extract clean markdown text from a JS-rendered URL using Crawl4AI.

    Returns extracted markdown text or None if Crawl4AI is unavailable.
    """
    try:
        from crawl4ai import AsyncWebCrawler  # type: ignore
        async with AsyncWebCrawler(verbose=False) as crawler:
            result = await crawler.arun(url=url)
            if result.success:
                return result.markdown[:3000]
            return None
    except ImportError:
        logger.warning("crawl4ai.not_installed", url=url)
        return None
    except Exception as exc:
        logger.error("crawl4ai.fetch_failed", url=url, error=str(exc))
        return None


async def _fallback_httpx(url: str) -> Optional[str]:
    """Raw httpx fetch fallback when Crawl4AI is not available."""
    import httpx
    try:
        async with httpx.AsyncClient(
            headers={"User-Agent": "DavisionAI-TechRadar/1.0"},
            follow_redirects=True,
            timeout=20.0,
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.text[:3000]
    except Exception as exc:
        logger.error("crawl4ai_fallback.failed", url=url, error=str(exc))
        return None


async def fetch_js_rendered_source(
    source_url: str,
    source_name: SourceName,
    title_hint: str = "JS-Rendered Source",
) -> list[ScoutOutput]:
    """
    Fetch and extract content from a JS-rendered page.

    Tries Crawl4AI first, falls back to httpx for static content.

    Args:
        source_url: Target URL to scrape.
        source_name: Source classification (SourceName enum).
        title_hint: Fallback title prefix for extracted items.

    Returns:
        List of ScoutOutput items (may be empty on failure).
    """
    logger.info("crawl4ai.fetch_start", url=source_url)

    content = await _try_crawl4ai(source_url)
    if not content:
        content = await _fallback_httpx(source_url)

    if not content or len(content.strip()) < 100:
        logger.warning("crawl4ai.empty_result", url=source_url)
        return []

    try:
        item = ScoutOutput(
            source_name=source_name,
            url=source_url,
            title=f"{title_hint} — {source_url.split('/')[-1] or 'Page'}",
            author=None,
            published_at=datetime.now(tz=timezone.utc),
            raw_content=content,
        )
        return [item]
    except Exception as exc:
        logger.error("crawl4ai.schema_failed", url=source_url, error=str(exc))
        return []


async def fetch_all_js_sources() -> list[ScoutOutput]:
    """
    Fetch all configured JS-rendered sources concurrently.

    Returns:
        Combined list of ScoutOutput items from all JS sources.
    """
    tasks = [
        fetch_js_rendered_source(
            source_url=s["url"],
            source_name=s["source_name"],
            title_hint=s["name"].replace("_", " ").title(),
        )
        for s in JS_SOURCES
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_items: list[ScoutOutput] = []
    for result in results:
        if isinstance(result, Exception):
            logger.error("crawl4ai.source_failed", error=str(result))
        else:
            all_items.extend(result)

    return all_items
