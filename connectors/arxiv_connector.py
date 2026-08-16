"""
connectors/arxiv_connector.py — ArXiv API connector.

Fetches recent papers from cs.CV, cs.CL, cs.LG, cs.AI categories
published within the last N hours using the ArXiv Atom feed API.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any
from xml.etree import ElementTree as ET

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from core.schemas import ScoutOutput, SourceName

ARXIV_API_URL = "http://export.arxiv.org/api/query"
ARXIV_NAMESPACE = "http://www.w3.org/2005/Atom"
ARXIV_NS = {"atom": ARXIV_NAMESPACE, "arxiv": "http://arxiv.org/schemas/atom"}

DEFAULT_CATEGORIES = ["cs.CV", "cs.CL", "cs.LG", "cs.AI"]
MAX_RESULTS_PER_CATEGORY = 50


@retry(
    retry=retry_if_exception_type(httpx.HTTPError),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(3),
    reraise=True,
)
async def _fetch_category(
    client: httpx.AsyncClient,
    category: str,
    max_results: int,
    since_hours: int,
) -> list[ScoutOutput]:
    """Fetch papers from a single ArXiv category."""
    params = {
        "search_query": f"cat:{category}",
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": max_results,
    }

    response = await client.get(ARXIV_API_URL, params=params, timeout=30.0)
    response.raise_for_status()

    root = ET.fromstring(response.text)
    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=since_hours)

    results: list[ScoutOutput] = []
    for entry in root.findall("atom:entry", ARXIV_NS):
        url_el = entry.find("atom:id", ARXIV_NS)
        title_el = entry.find("atom:title", ARXIV_NS)
        summary_el = entry.find("atom:summary", ARXIV_NS)
        published_el = entry.find("atom:published", ARXIV_NS)

        if url_el is None or title_el is None or summary_el is None:
            continue

        url = url_el.text.strip() if url_el.text else ""
        # Normalize to abs URL
        url = url.replace("http://arxiv.org/abs/", "https://arxiv.org/abs/")

        # Parse publish date
        published_at: datetime | None = None
        if published_el is not None and published_el.text:
            try:
                published_at = datetime.fromisoformat(
                    published_el.text.strip().replace("Z", "+00:00")
                )
            except ValueError:
                pass

        # Time filter — only process recent papers
        if published_at and published_at < cutoff:
            continue

        # Authors
        authors = [
            a.find("atom:name", ARXIV_NS).text.strip()
            for a in entry.findall("atom:author", ARXIV_NS)
            if a.find("atom:name", ARXIV_NS) is not None
        ]
        author = ", ".join(authors[:3])
        if len(authors) > 3:
            author += " et al."

        raw_content = f"{title_el.text.strip()}\n\n{summary_el.text.strip()}"

        try:
            results.append(
                ScoutOutput(
                    source_name=SourceName.ARXIV,
                    url=url,
                    title=title_el.text.strip(),
                    author=author or None,
                    published_at=published_at,
                    raw_content=raw_content,
                )
            )
        except Exception:
            continue  # Skip malformed entries

    return results


async def fetch_arxiv_papers(
    categories: list[str] = DEFAULT_CATEGORIES,
    max_results_per_category: int = MAX_RESULTS_PER_CATEGORY,
    since_hours: int = 24,
) -> list[ScoutOutput]:
    """
    Fetch recent ArXiv papers from multiple categories concurrently.

    Args:
        categories: List of ArXiv category codes (e.g. ['cs.CV', 'cs.CL']).
        max_results_per_category: Max results to fetch per category.
        since_hours: Only include papers published within this many hours.

    Returns:
        Deduplicated list of ScoutOutput objects.
    """
    async with httpx.AsyncClient(
        headers={"User-Agent": "DavisionAI-TechRadar/1.0 (research aggregator)"},
        http2=True,
    ) as client:
        tasks = [
            _fetch_category(client, cat, max_results_per_category, since_hours)
            for cat in categories
        ]
        results_per_cat = await asyncio.gather(*tasks, return_exceptions=True)

    # Flatten and deduplicate by URL
    seen_urls: set[str] = set()
    all_results: list[ScoutOutput] = []
    for result in results_per_cat:
        if isinstance(result, Exception):
            continue  # Log and continue — don't crash on one failed category
        for item in result:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                all_results.append(item)

    return all_results
