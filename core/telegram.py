"""
core/telegram.py — Telegram Bot API helper with MarkdownV2 escaping and retry logic.

Telegram MarkdownV2 requires escaping these 20 special characters:
_ * [ ] ( ) ~ ` > # + - = | { } . !  \
"""
from __future__ import annotations

import json
import re
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

# All special chars that MUST be escaped in MarkdownV2
_MDV2_SPECIAL = re.compile(r"([_*\[\]()~`>#\+\-=|{}.!\\])")


def escape_markdownv2(text: str) -> str:
    """Escape all Telegram MarkdownV2 special characters."""
    return _MDV2_SPECIAL.sub(r"\\\1", text)


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
    Build a Telegram MarkdownV2 formatted message for an article.

    Template:
    ━━━━━━━━━━━━━━━━━━━━━━━━
    🔥 **[SCORE]** | Category
    📋 Title
    ━━━━━━━━━━━━━━━━━━━━━━━━
    • Bullet 1
    • Bullet 2
    • Bullet 3
    🏷 Tags
    🔗 Read More
    """
    emoji = _score_emoji(article.relevance_score)
    score_str = f"{article.relevance_score:.1f}"
    sep = escape_markdownv2("━" * 28)

    title = escape_markdownv2(article.title)
    category = escape_markdownv2(article.primary_category)
    tags_str = escape_markdownv2(" · ".join(f"#{t}" for t in article.tags[:5]))
    url = escape_markdownv2(article.url)

    bullets = "\n".join(
        f"• {escape_markdownv2(b)}" for b in article.summary_bullets
    )

    published = ""
    if article.published_at:
        published = f"\n📅 {escape_markdownv2(article.published_at.strftime('%d %b %Y'))}"

    message = (
        f"{sep}\n"
        f"{emoji} *Skor: {escape_markdownv2(score_str)}* \\| {category}\n"
        f"{sep}\n\n"
        f"📋 *{title}*{published}\n\n"
        f"{bullets}\n\n"
        f"🏷 {tags_str}\n"
        f"🔗 [Makaleyi Oku]({url})"
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
    Send a Telegram MarkdownV2 message via Bot API.

    Retries up to 3 times with exponential backoff on HTTP errors.
    Returns the full Telegram API response dict.
    """
    settings = get_settings()
    token = settings.telegram_bot_token
    target_chat = chat_id or settings.telegram_chat_id

    if not token or not target_chat:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env"
        )

    # Guard against placeholder tokens from the example .env file.
    # These tokens produce a Telegram 404 Not Found and waste retry budget.
    _PLACEHOLDER_MARKERS = ("123456789", "AABBcc", "AABBccDDeeFF")
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
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": False,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()
