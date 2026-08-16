"""
agents/scout_agent.py — Scout Agent: Data Harvesting Pipeline.

Responsibilities:
1. Run all source connectors concurrently (ArXiv, Medium, GitHub).
2. Optionally include Crawl4AI for JS-rendered sources (set USE_CRAWL4AI=True).
3. Enforce URL deduplication against PostgreSQL before downstream processing.
4. Apply lightweight content cleaning.
5. Return validated ScoutOutput list for the Analyzer Agent.

Extension point:
  To add Crawl4AI/Playwright JS-rendered sources:
    Set USE_CRAWL4AI = True below, then add `fetch_all_js_sources` to the
    asyncio.gather() call in run_scout().
"""
from __future__ import annotations

import asyncio
import hashlib
import re

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from connectors.arxiv_connector import fetch_arxiv_papers
from connectors.github_connector import fetch_github_trending
from connectors.medium_connector import fetch_medium_articles
from core.database import get_session
from core.models import Article
from core.schemas import ScoutOutput

# ─────────────────────────────────────────────────────────────────────────────
# Optional: Crawl4AI connector for JS-rendered sources
# Set to True to include HuggingFace Papers + Papers With Code
# ─────────────────────────────────────────────────────────────────────────────
USE_CRAWL4AI = False

if USE_CRAWL4AI:
    from connectors.crawl4ai_connector import fetch_all_js_sources

logger = structlog.get_logger(__name__)

# Regex patterns for cleaning raw text
_WHITESPACE_RE = re.compile(r"\s+")
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_URL_RE = re.compile(r"https?://\S+")


def clean_text(raw: str) -> str:
    """
    Remove HTML tags, collapse whitespace, strip leading/trailing spaces.
    Preserves URLs so they can be indexed by the analyzer.
    """
    text = _HTML_TAG_RE.sub(" ", raw)
    text = _WHITESPACE_RE.sub(" ", text)
    return text.strip()


def content_hash(text: str) -> str:
    """SHA-256 hash of content for exact duplicate detection."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


async def _get_existing_urls(session: AsyncSession) -> set[str]:
    """Fetch all known article URLs from PostgreSQL for deduplication."""
    result = await session.execute(select(Article.url))
    return {row[0] for row in result.fetchall()}


async def run_scout(
    since_hours: int = 24,
) -> list[ScoutOutput]:
    """
    Execute the Scout Agent pipeline.

    Steps:
      1. Fetch from all connectors concurrently.
      2. Load existing URLs from PostgreSQL.
      3. Filter out already-known URLs (deduplication).
      4. Clean content text.
      5. Return validated ScoutOutput list.

    Args:
        since_hours: Time window in hours to look back for ArXiv papers.

    Returns:
        List of new, cleaned ScoutOutput items ready for the Analyzer.
    """
    logger.info("scout.start", since_hours=since_hours)

    # ── Step 1: Concurrent source fetching ───────────────────────────────────
    arxiv_task = asyncio.create_task(
        fetch_arxiv_papers(since_hours=since_hours),
        name="arxiv_fetch",
    )
    medium_task = asyncio.create_task(
        fetch_medium_articles(),
        name="medium_fetch",
    )
    github_task = asyncio.create_task(
        fetch_github_trending(),
        name="github_fetch",
    )

    arxiv_results, medium_results, github_results = await asyncio.gather(
        arxiv_task, medium_task, github_task, return_exceptions=True
    )

    raw_items: list[ScoutOutput] = []
    for source_name, result in [
        ("arxiv", arxiv_results),
        ("medium", medium_results),
        ("github", github_results),
    ]:
        if isinstance(result, Exception):
            logger.error(
                "scout.connector_failed",
                source=source_name,
                error=str(result),
            )
        else:
            raw_items.extend(result)
            logger.info(
                "scout.connector_success",
                source=source_name,
                count=len(result),
            )

    logger.info("scout.raw_total", count=len(raw_items))

    # ── Step 2: URL deduplication against PostgreSQL ──────────────────────────
    async with get_session() as session:
        existing_urls = await _get_existing_urls(session)

    new_items = [item for item in raw_items if item.url not in existing_urls]
    skipped = len(raw_items) - len(new_items)
    logger.info("scout.dedup", new=len(new_items), skipped=skipped)

    # ── Step 3: Content cleaning ──────────────────────────────────────────────
    cleaned_items: list[ScoutOutput] = []
    for item in new_items:
        cleaned_content = clean_text(item.raw_content)
        if len(cleaned_content) < 50:
            logger.debug("scout.skip_too_short", url=item.url)
            continue
        cleaned_items.append(
            item.model_copy(update={"raw_content": cleaned_content})
        )

    logger.info("scout.complete", output_count=len(cleaned_items))
    return cleaned_items
