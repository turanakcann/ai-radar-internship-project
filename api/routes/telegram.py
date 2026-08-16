"""api/routes/telegram.py — Telegram Webhook endpoint (inbound updates).

Receives Telegram Update payloads via POST /api/telegram/webhook.
Supported commands:
  /run  — triggers the full Scout -> Analyzer -> Dispatcher pipeline
          as a background task and replies with a confirmation message.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx
from fastapi import APIRouter, BackgroundTasks, Request, Response

from core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()

# ── Pydantic-free Telegram Update parsing ─────────────────────────────────────
# We parse the raw JSON manually so this file has zero extra dependencies and
# works even if the Telegram schema changes in minor ways.


def _extract_command(update: dict[str, Any]) -> tuple[str | None, str | None]:
    """Return (command_text, chat_id_str) from a Telegram Update dict."""
    message = update.get("message") or update.get("channel_post")
    if not message:
        return None, None
    text: str = message.get("text", "").strip()
    chat_id: str | None = str(message["chat"]["id"]) if "chat" in message else None
    return text, chat_id


async def _send_reply(token: str, chat_id: str, text: str) -> None:
    """Fire-and-forget HTML reply back to the Telegram chat."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                logger.warning(
                    "telegram_reply_failed",
                    extra={"status": resp.status_code, "body": resp.text},
                )
    except Exception as exc:
        logger.error("telegram_reply_error", extra={"error": str(exc)})


# ── Shared pipeline-running state (same flag as trigger.py) ──────────────────
# Imported lazily to avoid circular imports at module load time.

async def _run_pipeline_background(reply_chat_id: str, token: str) -> None:
    """Run the pipeline and notify the user when done (or on error)."""
    try:
        from agents.orchestrator import run_pipeline
        await run_pipeline()
        await _send_reply(
            token,
            reply_chat_id,
            "Pipeline tamamlandi! Yeni makaleler islendi.",
        )
    except Exception as exc:
        logger.error("webhook_pipeline_error", extra={"error": str(exc)})
        await _send_reply(
            token,
            reply_chat_id,
            f"Pipeline hatasi olustu: <code>{str(exc)[:200]}</code>",
        )


# ── Webhook endpoint ──────────────────────────────────────────────────────────

@router.post("/webhook", status_code=200)
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
) -> Response:
    """
    Receive a Telegram Update and dispatch inbound commands.

    Telegram requires a 200 response within ~5 seconds or it will
    retry the delivery. We return immediately and run the pipeline
    as a BackgroundTask so the response is never delayed.
    """
    settings = get_settings()
    token = settings.telegram_bot_token

    # Parse the incoming JSON update
    try:
        update: dict[str, Any] = await request.json()
    except Exception:
        # Return 200 even on parse error — prevents Telegram from spam-retrying
        logger.warning("telegram_webhook_invalid_json")
        return Response(status_code=200)

    logger.info("telegram_webhook_received", extra={"update_id": update.get("update_id")})

    command, chat_id = _extract_command(update)

    # Only handle the /run command; silently ignore everything else
    if command == "/run" and chat_id:
        # Check if pipeline is already running via the trigger module's flag
        from api.routes import trigger as _trigger_mod
        if _trigger_mod._pipeline_running:
            await _send_reply(
                token,
                chat_id,
                "Pipeline zaten calisiyor, lutfen bekleyin.",
            )
        else:
            # Immediate acknowledgement
            await _send_reply(
                token,
                chat_id,
                "Pipeline basladi! Tamamlandiginda bildirim alacaksiniz.",
            )
            # Run the heavy work in the background
            background_tasks.add_task(
                _run_pipeline_background,
                reply_chat_id=chat_id,
                token=token,
            )

    # Always return 200 to Telegram
    return Response(status_code=200)
