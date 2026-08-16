"""
agents/dispatcher_agent.py — Dispatcher Agent: Telegram Notification Engine.

Queries PostgreSQL for high-relevance articles not yet dispatched,
formats them as Telegram MarkdownV2 messages, sends via Bot API,
and marks them as dispatched in the database.
"""
from __future__ import annotations

from datetime import datetime, timezone

import structlog
from sqlalchemy import and_, select, update
from sqlalchemy.orm import selectinload

from core.config import get_settings
from core.database import get_session
from core.models import Article, Source, TelegramDispatch
from core.schemas import DispatchResult, DispatcherInput
from core.telegram import format_telegram_message, send_telegram_message

logger = structlog.get_logger(__name__)


async def _fetch_pending_articles(
    min_score: float,
) -> list[Article]:
    """
    Fetch articles with relevance_score >= min_score AND is_dispatched = FALSE.
    Ordered by relevance_score descending.
    """
    async with get_session() as session:
        result = await session.execute(
            select(Article)
            .options(selectinload(Article.source))
            .where(
                and_(
                    Article.relevance_score >= min_score,
                    Article.is_dispatched.is_(False),
                    Article.summary_bullets.isnot(None),
                )
            )
            .order_by(Article.relevance_score.desc())
        )
        return list(result.scalars().all())


async def _mark_dispatched(
    article_id: int,
    message_id: int | None,
    chat_id: str,
    payload: str,
    status: str,
    error: str | None = None,
    attempt_count: int = 1,
) -> None:
    """Update dispatch state in PostgreSQL."""
    async with get_session() as session:
        # Update article is_dispatched flag (only on success)
        if status == "success":
            await session.execute(
                update(Article)
                .where(Article.id == article_id)
                .values(
                    is_dispatched=True,
                    dispatched_at=datetime.now(tz=timezone.utc),
                )
            )

        # Insert dispatch log
        dispatch = TelegramDispatch(
            article_id=article_id,
            chat_id=chat_id,
            message_id=message_id,
            payload=payload,
            status=status,
            attempt_count=attempt_count,
            last_error=error,
            sent_at=datetime.now(tz=timezone.utc) if status == "success" else None,
        )
        session.add(dispatch)


async def dispatch_article(article: Article) -> DispatchResult:
    """
    Format and send a single article to Telegram.
    Returns a DispatchResult indicating success or failure.
    """
    settings = get_settings()

    dispatch_input = DispatcherInput(
        article_id=article.id,
        url=article.url,
        title=article.title,
        author=article.author,
        published_at=article.published_at,
        relevance_score=float(article.relevance_score or 0),
        primary_category=article.primary_category or "AI/ML",
        tags=list(article.tags or []),
        summary_bullets=list(article.summary_bullets or []),
    )

    message_text = format_telegram_message(dispatch_input)
    chat_id = settings.telegram_chat_id
    attempt_count = 0
    last_error: str | None = None

    try:
        response = await send_telegram_message(message_text, chat_id=chat_id)
        attempt_count = 1
        telegram_message_id = response.get("result", {}).get("message_id")

        await _mark_dispatched(
            article_id=article.id,
            message_id=telegram_message_id,
            chat_id=chat_id,
            payload=message_text[:4000],
            status="success",
            attempt_count=attempt_count,
        )

        logger.info(
            "dispatcher.sent",
            article_id=article.id,
            score=dispatch_input.relevance_score,
            telegram_message_id=telegram_message_id,
        )

        return DispatchResult(
            article_id=article.id,
            success=True,
            telegram_message_id=telegram_message_id,
            attempt_count=attempt_count,
        )

    except Exception as exc:
        last_error = str(exc)
        attempt_count = 3  # max retries exhausted (tenacity handles retries)

        await _mark_dispatched(
            article_id=article.id,
            message_id=None,
            chat_id=chat_id,
            payload=message_text[:4000],
            status="failed",
            error=last_error,
            attempt_count=attempt_count,
        )

        logger.error(
            "dispatcher.failed",
            article_id=article.id,
            error=last_error,
        )

        return DispatchResult(
            article_id=article.id,
            success=False,
            attempt_count=attempt_count,
            error=last_error,
        )


async def run_dispatcher() -> list[DispatchResult]:
    """
    Execute the Dispatcher Agent pipeline.

    Steps:
      1. Query PostgreSQL for undispatched high-relevance articles.
      2. For each article: format → send → mark dispatched.
      3. Return results summary.
    """
    settings = get_settings()
    min_score = settings.relevance_threshold_dispatch

    logger.info("dispatcher.start", min_score=min_score)

    pending = await _fetch_pending_articles(min_score=min_score)
    logger.info("dispatcher.pending_count", count=len(pending))

    if not pending:
        logger.info("dispatcher.nothing_to_send")
        return []

    results: list[DispatchResult] = []
    for article in pending:
        result = await dispatch_article(article)
        results.append(result)

    success_count = sum(1 for r in results if r.success)
    fail_count = len(results) - success_count
    logger.info(
        "dispatcher.complete",
        sent=success_count,
        failed=fail_count,
    )
    return results
