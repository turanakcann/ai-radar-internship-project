"""
core/telegram.py — Telegram Bot API helper.

Uses HTML parse_mode instead of MarkdownV2.
HTML only requires escaping <, >, & — done once via html.escape().
This eliminates the 400 Bad Request errors caused by MarkdownV2's
strict 20-character escape rules breaking on dynamic article text.
"""
from __future__ import annotations

import html
from datetime import datetime

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from core.config import get_settings
from core.schemas import DispatcherInput


def _h(text: str) -> str:
    """Escape a string for safe inclusion in Telegram HTML messages."""
    return html.escape(str(text), quote=False)


def _score_emoji(score: float) -> str:
    if score >= 9.0:
        return "🔥🔥🔥"
    if score >= 8.0:
        return "🔥🔥"
    if score >= 7.5:
        return "🔥"
    return "⭐"


def format_telegram_message(article: DispatcherInput) -> str:
    """
    Build a Telegram HTML-formatted message for a high-relevance article.

    Template:
    ━━━━━━━━━━━━━━━━━━━━━━━━
    🔥 Skor: 8.5 | Category
    ━━━━━━━━━━━━━━━━━━━━━━━━
    📋 <b>Title</b>  📅 16 Aug 2026

    • Bullet 1
    • Bullet 2
    • Bullet 3

    🏷 #tag1 · #tag2
    🔗 <a href="url">Makaleyi Oku</a>
    """
    sep = "━" * 28
    emoji = _score_emoji(article.relevance_score)
    score_str = f"{article.relevance_score:.1f}"

    title = _h(article.title)
    category = _h(article.primary_category)
    tags_str = _h(" · ".join(f"#{t}" for t in article.tags[:5]))
    url = article.url  # URLs are not escaped — Telegram validates them separately

    bullets_html = "\n".join(
        f"• {_h(b)}" for b in article.summary_bullets
    )

    published_str = ""
    if article.published_at:
        published_str = f"  📅 {_h(article.published_at.strftime('%d %b %Y'))}"

    message = (
        f"{sep}\n"
        f"{emoji} <b>Skor: {_h(score_str)}</b> | {category}\n"
        f"{sep}\n\n"
        f"📋 <b>{title}</b>{published_str}\n\n"
        f"{bullets_html}\n\n"
        f"🏷 {tags_str}\n"
        f'🔗 <a href="{url}">Makaleyi Oku</a>'
    )
    return message


@retry(
    retry=retry_if_exception_type(httpx.HTTPError),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(3),
    reraise=True,
)
async def send_telegram_message(
    text: str,
    chat_id: str | None = None,
) -> dict:
    """
    Send an HTML-formatted message via the Telegram Bot API.

    Retries up to 3 times with exponential backoff on transient HTTP errors.
    Returns the full Telegram API response dict on success.
    """
    settings = get_settings()
    token = settings.telegram_bot_token
    target_chat = chat_id or settings.telegram_chat_id

    if not token or not target_chat:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env"
        )

    # Guard against placeholder tokens — they produce a Telegram 404 and
    # waste the retry budget without any chance of succeeding.
    _PLACEHOLDER_MARKERS = ("123456789", "AABBcc", "AABBccDDeeFF", "<YOUR_")
    if any(marker in token for marker in _PLACEHOLDER_MARKERS):
        import logging as _logging
        _logging.getLogger(__name__).warning(
            "TELEGRAM_BOT_TOKEN looks like a placeholder value — "
            "skipping HTTP send. Replace it with a real bot token from @BotFather."
        )
        raise ValueError(
            "Placeholder Telegram token detected. "
            "Set a real TELEGRAM_BOT_TOKEN in .env to enable dispatching."
        )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": target_chat,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
        "disable_notification": False,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

