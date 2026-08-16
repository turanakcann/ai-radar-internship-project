"""
core/models.py — SQLAlchemy ORM models mirroring the DB schema.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    base_url: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    articles: Mapped[list["Article"]] = relationship(back_populates="source")


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    source_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sources.id"), nullable=False
    )
    url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[Optional[str]] = mapped_column(Text)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    raw_content: Mapped[Optional[str]] = mapped_column(Text)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64))

    # Analyzer outputs
    relevance_score: Mapped[Optional[float]] = mapped_column(Numeric(4, 2))
    primary_category: Mapped[Optional[str]] = mapped_column(String(100))
    tags: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))
    summary_bullets: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))
    token_spent: Mapped[int] = mapped_column(Integer, default=0)

    # Dispatcher state
    is_dispatched: Mapped[bool] = mapped_column(Boolean, default=False)
    dispatched_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # ChromaDB reference
    chroma_doc_id: Mapped[Optional[str]] = mapped_column(Text)

    # Lifecycle
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    source: Mapped["Source"] = relationship(back_populates="articles")
    token_logs: Mapped[list["TokenLog"]] = relationship(back_populates="article")
    dispatches: Mapped[list["TelegramDispatch"]] = relationship(back_populates="article")


class TokenLog(Base):
    __tablename__ = "token_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    article_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("articles.id", ondelete="CASCADE")
    )
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    operation: Mapped[str] = mapped_column(String(50), nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[Optional[float]] = mapped_column(Numeric(12, 8))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    article: Mapped[Optional["Article"]] = relationship(back_populates="token_logs")


class TelegramDispatch(Base):
    __tablename__ = "telegram_dispatches"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    article_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False
    )
    chat_id: Mapped[str] = mapped_column(Text, nullable=False)
    message_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    payload: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    attempt_count: Mapped[int] = mapped_column(SmallInteger, default=0)
    last_error: Mapped[Optional[str]] = mapped_column(Text)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    article: Mapped["Article"] = relationship(back_populates="dispatches")


class RunLog(Base):
    __tablename__ = "run_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    run_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), server_default=func.uuid_generate_v4()
    )
    phase: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    articles_found: Mapped[int] = mapped_column(Integer, default=0)
    articles_saved: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
