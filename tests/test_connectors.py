"""
tests/test_connectors.py — Unit tests for source connectors.

Uses respx to mock HTTP responses without hitting real APIs.
"""
from __future__ import annotations

import pytest
import respx
import httpx
from datetime import datetime, timezone

from connectors.arxiv_connector import fetch_arxiv_papers, _fetch_category
from connectors.medium_connector import _strip_html, _parse_medium_date
from connectors.github_connector import _fetch_trending_page
from core.schemas import ScoutOutput, SourceName

# ─────────────────────────────────────────────────────────────────────────────
# ArXiv Connector Tests
# ─────────────────────────────────────────────────────────────────────────────

ARXIV_MOCK_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>https://arxiv.org/abs/2608.12345</id>
    <title>YOLOv12: Real-Time Object Detection with Edge AI Optimization</title>
    <summary>We propose YOLOv12, a novel architecture for real-time object detection
    optimized for edge devices. Our method achieves 30% faster inference with 50%
    less memory consumption compared to YOLOv11.</summary>
    <author><name>Jane Smith</name></author>
    <author><name>John Doe</name></author>
    <published>2026-08-08T10:00:00Z</published>
  </entry>
</feed>"""


@pytest.mark.asyncio
@respx.mock
async def test_arxiv_fetch_category():
    """Test ArXiv connector parses entries correctly."""
    respx.get("http://export.arxiv.org/api/query").mock(
        return_value=httpx.Response(200, text=ARXIV_MOCK_RESPONSE)
    )

    async with httpx.AsyncClient() as client:
        results = await _fetch_category(client, "cs.CV", max_results=10, since_hours=48)

    assert len(results) == 1
    assert results[0].source_name == SourceName.ARXIV
    assert "YOLOv12" in results[0].title
    assert results[0].author == "Jane Smith, John Doe"
    assert results[0].url == "https://arxiv.org/abs/2608.12345"


@pytest.mark.asyncio
@respx.mock
async def test_arxiv_handles_http_error():
    """Test ArXiv connector handles 429 rate limit gracefully."""
    respx.get("http://export.arxiv.org/api/query").mock(
        return_value=httpx.Response(429, text="Rate limited")
    )

    async with httpx.AsyncClient() as client:
        with pytest.raises(httpx.HTTPStatusError):
            await _fetch_category(client, "cs.CV", max_results=10, since_hours=24)


# ─────────────────────────────────────────────────────────────────────────────
# Medium Connector Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_strip_html_removes_tags():
    html = "<p>Hello <strong>World</strong>! <a href='#'>Link</a></p>"
    result = _strip_html(html)
    assert "<" not in result
    assert "Hello" in result
    assert "World" in result


def test_strip_html_collapses_whitespace():
    html = "<p>  Too   many   spaces  </p>"
    result = _strip_html(html)
    assert "  " not in result.strip()


def test_parse_medium_date_valid():
    date_str = "Thu, 08 Aug 2026 10:00:00 GMT"
    result = _parse_medium_date(date_str)
    assert result is not None
    assert result.year == 2026
    assert result.month == 8


def test_parse_medium_date_invalid():
    result = _parse_medium_date("not-a-date")
    assert result is None


def test_parse_medium_date_none():
    result = _parse_medium_date(None)
    assert result is None


# ─────────────────────────────────────────────────────────────────────────────
# ScoutOutput Schema Validation
# ─────────────────────────────────────────────────────────────────────────────

def test_scout_output_valid():
    item = ScoutOutput(
        source_name=SourceName.ARXIV,
        url="https://arxiv.org/abs/2608.99999",
        title="Test Paper on Computer Vision",
        author="Author Name",
        published_at=datetime.now(tz=timezone.utc),
        raw_content="This is the content of the paper about computer vision. " * 3,
    )
    assert item.source_name == SourceName.ARXIV
    assert item.url.startswith("https://")


def test_scout_output_invalid_url():
    with pytest.raises(Exception):
        ScoutOutput(
            source_name=SourceName.ARXIV,
            url="not-a-url",
            title="Test",
            raw_content="Some content " * 5,
        )


def test_scout_output_short_content():
    with pytest.raises(Exception):
        ScoutOutput(
            source_name=SourceName.MEDIUM,
            url="https://medium.com/test",
            title="Test Article",
            raw_content="Too short",  # min_length=50
        )
