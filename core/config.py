"""
core/config.py — Pydantic Settings for Davision AI Tech & Trend Radar.

All configuration is loaded from environment variables / .env file.
Validation fails fast at startup if required values are missing.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Database ─────────────────────────────────────────────────────────────
    database_url: str = Field(
        default="postgresql+asyncpg://radar:radar_secret@localhost:5432/tech_radar",
        description="Async PostgreSQL connection URL (asyncpg driver).",
    )

    # ── ChromaDB ─────────────────────────────────────────────────────────────
    chromadb_path: str = Field(default="./data/chromadb")
    chromadb_host: str = Field(default="")           # Set to hostname in Docker
    chromadb_port: int = Field(default=8001)
    chromadb_collection: str = Field(default="tech_radar_articles")

    @property
    def chromadb_use_http(self) -> bool:
        return bool(self.chromadb_host)

    # ── OpenAI ───────────────────────────────────────────────────────────────
    openai_api_key: str = Field(default="")
    openai_scoring_model: str = Field(default="gpt-4o-mini")
    openai_summary_model: str = Field(default="gpt-4o-mini")
    openai_embedding_model: str = Field(default="text-embedding-3-small")

    # ── Anthropic (fallback) ──────────────────────────────────────────────────
    anthropic_api_key: str = Field(default="")
    anthropic_model: str = Field(default="claude-haiku-20240307")

    # ── Telegram ─────────────────────────────────────────────────────────────
    telegram_bot_token: str = Field(default="")
    telegram_chat_id: str = Field(default="")

    # ── Scoring Thresholds ────────────────────────────────────────────────────
    relevance_threshold_summary: float = Field(default=6.0)
    relevance_threshold_dispatch: float = Field(default=7.5)

    # ── Scheduler ────────────────────────────────────────────────────────────
    schedule_interval_hours: int = Field(default=4)

    # ── API ──────────────────────────────────────────────────────────────────
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    frontend_origin: str = Field(default="http://localhost:3000")

    # ── Logging ──────────────────────────────────────────────────────────────
    log_level: str = Field(default="INFO")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in valid:
            raise ValueError(f"log_level must be one of {valid}")
        return upper


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings singleton."""
    return Settings()
