"""
core/schemas.py — Pydantic inter-agent communication schemas.

All data flowing between Scout → Analyzer → Dispatcher MUST be validated
against these schemas. No raw dicts allowed in agent handoffs.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────

class SourceName(str, Enum):
    ARXIV = "arxiv"
    MEDIUM = "medium"
    GITHUB = "github"


class PrimaryCategory(str, Enum):
    COMPUTER_VISION = "Computer Vision"
    NLP = "Natural Language Processing"
    LLM = "Large Language Models"
    EDGE_AI = "Edge AI"
    ROBOTICS = "Robotics"
    GENERATIVE_AI = "Generative AI"
    MLOps = "MLOps"
    MULTIMODAL = "Multimodal AI"
    OTHER = "Other AI/ML"


class FilterDecision(str, Enum):
    PASS = "pass"
    DISCARD = "discard"


# ─────────────────────────────────────────────────────────────────────────────
# Scout Agent Output
# ─────────────────────────────────────────────────────────────────────────────

class ScoutOutput(BaseModel):
    """Raw harvested item from a source connector."""
    source_name: SourceName
    url: str                                     # validated as string to allow GitHub URLs
    title: str = Field(min_length=3, max_length=500)
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    raw_content: str = Field(min_length=50)

    @field_validator("url")
    @classmethod
    def url_must_be_non_empty(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith("http"):
            raise ValueError("url must start with http")
        return v


# ─────────────────────────────────────────────────────────────────────────────
# Analyzer Agent
# ─────────────────────────────────────────────────────────────────────────────

class KeywordFilterResult(BaseModel):
    """Result of T0 heuristic keyword check."""
    decision: FilterDecision
    matched_keywords: list[str] = Field(default_factory=list)
    token_spent: int = 0


class ScoringResult(BaseModel):
    """Result of T1 LLM relevance scoring."""
    relevance_score: float = Field(ge=0.0, le=10.0)
    primary_category: PrimaryCategory
    reasoning: str
    token_spent: int


class SummaryResult(BaseModel):
    """Result of T2 Turkish executive summary generation."""
    bullets: list[str] = Field(min_length=3, max_length=3)
    tags: list[str] = Field(default_factory=list)
    token_spent: int

    @field_validator("bullets")
    @classmethod
    def validate_bullets(cls, v: list[str]) -> list[str]:
        if len(v) != 3:
            raise ValueError("summary_bullets must contain exactly 3 items")
        return v


class AnalyzerOutput(BaseModel):
    """Full analyzer result persisted to PostgreSQL + ChromaDB."""
    article_id: Optional[int] = None           # set after DB insert
    source_name: SourceName
    url: str
    title: str
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    relevance_score: float = Field(ge=0.0, le=10.0)
    primary_category: PrimaryCategory
    tags: list[str] = Field(default_factory=list)
    summary_bullets: list[str] = Field(default_factory=list)
    token_spent: int = 0
    filter_decision: FilterDecision
    chroma_doc_id: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# Dispatcher Agent
# ─────────────────────────────────────────────────────────────────────────────

class DispatcherInput(BaseModel):
    """High-score article ready for Telegram dispatch."""
    article_id: int
    url: str
    title: str
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    relevance_score: float
    primary_category: str
    tags: list[str]
    summary_bullets: list[str]


class DispatchResult(BaseModel):
    """Result of a Telegram dispatch attempt."""
    article_id: int
    success: bool
    telegram_message_id: Optional[int] = None
    attempt_count: int
    error: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# API Response Models
# ─────────────────────────────────────────────────────────────────────────────

class ArticleResponse(BaseModel):
    """Public API representation of an article."""
    id: int
    source_name: str
    url: str
    title: str
    author: Optional[str]
    published_at: Optional[datetime]
    relevance_score: Optional[float]
    primary_category: Optional[str]
    tags: list[str]
    summary_bullets: list[str]
    is_dispatched: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class SearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=500)
    top_k: int = Field(default=10, ge=1, le=50)
    min_score: float = Field(default=0.0, ge=0.0, le=10.0)


class SearchResult(BaseModel):
    article: ArticleResponse
    similarity_score: float


class PipelineStats(BaseModel):
    total_articles: int
    articles_by_source: dict[str, int]
    articles_by_category: dict[str, int]
    total_tokens_spent: int
    total_cost_usd: float
    dispatched_count: int
    daily_ingestion: list[dict]


class RunTriggerResponse(BaseModel):
    run_id: str
    status: str
    message: str
