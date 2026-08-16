"""
connectors/medium_connector.py — Medium RSS feed connector.

Fetches articles from Medium's RSS feeds for AI/ML tags.
Uses feedparser for lightweight parsing (no Playwright required).
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Optional

import feedparser
import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from core.schemas import ScoutOutput, SourceName

# Medium RSS feed URLs for AI/ML tags
MEDIUM_RSS_FEEDS = [
    "https://medium.com/feed/tag/artificial-intelligence",
    "https://medium.com/feed/tag/machine-learning",
    "https://medium.com/feed/tag/computer-vision",
    "https://medium.com/feed/tag/deep-learning",
    "https://medium.com/feed/tag/large-language-models",
    "https://medium.com/feed/tag/generative-ai",
]


def _parse_medium_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse RFC 2822 date string from RSS to timezone-aware datetime."""
    if not date_str:
        return None
    try:
        return parsedate_to_datetime(date_str).astimezone(timezone.utc)
    except Exception:
        return None


def _strip_html(html: str) -> str:
    """Very lightweight HTML tag stripper for RSS summaries."""
    import re
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:2000]  # Cap content length


@retry(
    retry=retry_if_exception_type(httpx.HTTPError),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(3),
    reraise=True,
)
async def _fetch_feed(
    client: httpx.AsyncClient,
    feed_url: str,
) -> list[ScoutOutput]:
    """Fetch and parse a single Medium RSS feed."""
    response = await client.get(feed_url, timeout=20.0)
    response.raise_for_status()

    feed = feedparser.parse(response.text)
    results: list[ScoutOutput] = []

    for entry in feed.entries:
        url = entry.get("link", "").strip()
        title = entry.get("title", "").strip()
        author = entry.get("author", "").strip() or None

        # Extract content: prefer content over summary
        content = ""
        if hasattr(entry, "content") and entry.content:
            content = _strip_html(entry.content[0].get("value", ""))
        elif hasattr(entry, "summary"):
            content = _strip_html(entry.summary)

        published_at = _parse_medium_date(
            entry.get("published") or entry.get("updated")
        )

        if not url or not title or len(content) < 50:
            continue

        try:
            results.append(
                ScoutOutput(
                    source_name=SourceName.MEDIUM,
                    url=url,
                    title=title,
                    author=author,
                    published_at=published_at,
                    raw_content=f"{title}\n\n{content}",
                )
            )
        except Exception:
            continue

    return results


async def fetch_medium_articles(
    feeds: list[str] = MEDIUM_RSS_FEEDS,
) -> list[ScoutOutput]:
    """
    Fetch articles from multiple Medium RSS feeds concurrently.

    Returns:
        Deduplicated list of ScoutOutput objects.
    """
    async with httpx.AsyncClient(
        headers={"User-Agent": "DavisionAI-TechRadar/1.0 (research aggregator)"},
        follow_redirects=True,
    ) as client:
        tasks = [_fetch_feed(client, feed_url) for feed_url in feeds]
        results_per_feed = await asyncio.gather(*tasks, return_exceptions=True)

    seen_urls: set[str] = set()
    all_results: list[ScoutOutput] = []
    for result in results_per_feed:
        if isinstance(result, Exception):
            continue
        for item in result:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                all_results.append(item)

    return all_results
