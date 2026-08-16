"""
connectors/github_connector.py — GitHub Trending Repositories Scraper.

Scrapes https://github.com/trending/{language}?since=daily
using httpx + BeautifulSoup for lightweight HTML parsing.
No GitHub API token required for trending page.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Optional

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from core.schemas import ScoutOutput, SourceName

GITHUB_TRENDING_BASE = "https://github.com/trending"

# AI/ML relevant languages to scrape
TARGET_LANGUAGES = ["python", "c++", "jupyter-notebook", "rust"]
SINCE_OPTIONS = ["daily", "weekly"]

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
}


@retry(
    retry=retry_if_exception_type(httpx.HTTPError),
    wait=wait_exponential(multiplier=2, min=3, max=60),
    stop=stop_after_attempt(3),
    reraise=True,
)
async def _fetch_trending_page(
    client: httpx.AsyncClient,
    language: str,
    since: str,
) -> list[ScoutOutput]:
    """Fetch and parse a single GitHub Trending page."""
    url = f"{GITHUB_TRENDING_BASE}/{language}?since={since}"
    response = await client.get(url, timeout=30.0)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    articles = soup.find_all("article", class_="Box-row")

    results: list[ScoutOutput] = []
    for article in articles:
        # Repo URL
        h2 = article.find("h2")
        if not h2:
            continue
        link_tag = h2.find("a")
        if not link_tag or not link_tag.get("href"):
            continue

        repo_path = link_tag["href"].strip().lstrip("/")
        repo_url = f"https://github.com/{repo_path}"
        repo_name = repo_path.replace("/", " / ")

        # Description
        desc_tag = article.find("p")
        description = desc_tag.get_text(strip=True) if desc_tag else ""

        # Stars today
        stars_today_tag = article.find("span", class_="d-inline-block float-sm-right")
        stars_today = stars_today_tag.get_text(strip=True) if stars_today_tag else ""

        # Total stars
        stars_tag = article.find("a", href=lambda h: h and h.endswith("/stargazers"))
        total_stars = stars_tag.get_text(strip=True) if stars_tag else ""

        # Built by (contributors)
        built_by = article.find("span", string=lambda s: s and "Built by" in s)
        contributors = ""
        if built_by:
            contributors_tags = article.find_all("a", attrs={"data-hovercard-type": "user"})
            contributors = ", ".join(a.get("aria-label", "") for a in contributors_tags[:3])

        raw_content = (
            f"Repository: {repo_name}\n"
            f"Language: {language.title()}\n"
            f"Description: {description}\n"
            f"Total Stars: {total_stars}\n"
            f"Stars Today: {stars_today}\n"
            f"Contributors: {contributors}\n"
            f"Trending Period: {since}\n"
            f"URL: {repo_url}"
        )

        if len(description) < 10:
            continue  # Skip repos with no description

        try:
            results.append(
                ScoutOutput(
                    source_name=SourceName.GITHUB,
                    url=repo_url,
                    title=f"[GitHub Trending] {repo_name}",
                    author=contributors or None,
                    published_at=datetime.now(tz=timezone.utc),
                    raw_content=raw_content,
                )
            )
        except Exception:
            continue

    return results


async def fetch_github_trending(
    languages: list[str] = TARGET_LANGUAGES,
    since: str = "daily",
) -> list[ScoutOutput]:
    """
    Fetch trending GitHub repositories for AI-relevant languages.

    Returns:
        Deduplicated list of ScoutOutput objects.
    """
    async with httpx.AsyncClient(
        headers=_HEADERS,
        follow_redirects=True,
        http2=True,
    ) as client:
        tasks = [
            _fetch_trending_page(client, lang, since)
            for lang in languages
        ]
        results_per_lang = await asyncio.gather(*tasks, return_exceptions=True)

    seen_urls: set[str] = set()
    all_results: list[ScoutOutput] = []
    for result in results_per_lang:
        if isinstance(result, Exception):
            continue
        for item in result:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                all_results.append(item)

    return all_results
