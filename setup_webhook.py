"""
setup_webhook.py — Register a Telegram Webhook URL with the Bot API.

Usage:
    .\venv\Scripts\python setup_webhook.py

The script will prompt for your public URL (e.g. from ngrok) and register
it as the webhook for TELEGRAM_BOT_TOKEN loaded from .env.

Webhook will be set to:  <YOUR_URL>/api/telegram/webhook
"""
import os
import sys
from pathlib import Path

# ── Load .env ─────────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)
except ImportError:
    # Manual fallback if python-dotenv is not installed
    with open(Path(__file__).parent / ".env") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, _, v = ln.partition("=")
                os.environ.setdefault(k.strip(), v.strip())

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
if not BOT_TOKEN or "<YOUR_" in BOT_TOKEN:
    print("[ERROR] TELEGRAM_BOT_TOKEN is not set or is still a placeholder in .env")
    sys.exit(1)

print(f"[INFO] Bot token loaded: {BOT_TOKEN[:12]}...")

# ── Prompt for public URL ─────────────────────────────────────────────────────
print()
print("Enter your public base URL (e.g. from ngrok or a deployed server).")
print("Example:  https://abc123.ngrok-free.app")
print("Example:  https://api.yourproject.com")
print()
base_url = input("Public URL: ").strip().rstrip("/")

if not base_url.startswith("http"):
    print("[ERROR] URL must start with http:// or https://")
    sys.exit(1)

webhook_url = f"{base_url}/api/telegram/webhook"
print(f"\n[INFO] Registering webhook: {webhook_url}")

# ── Call Telegram setWebhook ──────────────────────────────────────────────────
try:
    import httpx
except ImportError:
    print("[ERROR] httpx not installed — run: pip install httpx")
    sys.exit(1)

import asyncio

async def register_webhook():
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    params = {
        "url": webhook_url,
        "allowed_updates": ["message", "channel_post"],
        "drop_pending_updates": True,
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(api_url, json=params)

    data = response.json()
    if response.status_code == 200 and data.get("ok"):
        print()
        print("Webhook registered successfully!")
        print(f"  URL      : {webhook_url}")
        print(f"  Response : {data.get('description', 'Webhook was set')}")
        print()
        print("Next steps:")
        print("  1. Keep your FastAPI server running (uvicorn api.main:app --reload)")
        print("  2. Keep your public tunnel running (ngrok http 8000)")
        print("  3. Send  /run  to your Telegram bot or channel")
        print("     The bot will reply and trigger the pipeline.")
    else:
        print()
        print(f"[ERROR] Telegram API returned an error:")
        print(f"  HTTP {response.status_code}: {data}")
        sys.exit(1)

asyncio.run(register_webhook())
