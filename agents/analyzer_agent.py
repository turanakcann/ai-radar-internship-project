"""
agents/analyzer_agent.py — Analyzer Agent: Token-Optimized Intelligence Pipeline.

4-Tier Token Optimization Protocol:
  T0 (0 tokens)    — Heuristic keyword filter. Non-matching items discarded immediately.
  T1 (~150 tokens) — GPT-4o-mini relevance scoring (0.0 – 10.0).
  T2 (~300 tokens) — Turkish 3-bullet executive summary (only if score >= threshold).
  T3 (~50 tokens)  — text-embedding-3-small vector generation (only if score >= threshold).

Total token spend is logged to the token_logs table for analytics.
"""
from __future__ import annotations

import asyncio
import json
import re
import uuid
from datetime import datetime, timezone
from typing import Optional

import structlog
from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.chromadb_client import upsert_article_vector
from core.config import Settings, get_settings
from core.database import get_session
from core.models import Article, Source, TokenLog
from core.schemas import (
    AnalyzerOutput,
    FilterDecision,
    KeywordFilterResult,
    PrimaryCategory,
    ScoutOutput,
    ScoringResult,
    SummaryResult,
    SourceName,
)

logger = structlog.get_logger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# T0 — Keyword Whitelist (Heuristic Filter)
# ─────────────────────────────────────────────────────────────────────────────

AI_KEYWORDS = [
    # Core AI/ML
    r"\bLLM\b", r"\bRAG\b", r"\bGPT\b", r"\bLlama\b", r"\bClaude\b",
    r"\btransformer\b", r"\battention\b", r"\bfine.tun", r"\bfoundation model",
    r"\bpre.train", r"\binstruct.tun",
    # Computer Vision
    r"\bYOLO\b", r"\bcomputer vision\b", r"\bobject detection\b",
    r"\bsemantic segmentation\b", r"\binstance segmentation\b",
    r"\bimage classification\b", r"\bpose estimation\b", r"\bdepth estimation\b",
    r"\boptical flow\b", r"\bvision.language\b", r"\bVLM\b", r"\bVision Transformer\b",
    r"\bViT\b", r"\bDETR\b", r"\bSAM\b", r"\bsegment anything\b",
    # Generative AI
    r"\bdiffusion model\b", r"\bstable diffusion\b", r"\bGAN\b", r"\bVAE\b",
    r"\blatent diffusion\b", r"\btext.to.image\b", r"\bimage generation\b",
    r"\bmultimodal\b",
    # Edge AI / Deployment
    r"\bedge AI\b", r"\bedge computing\b", r"\bquantiz", r"\bpruning\b",
    r"\bknowledge distill", r"\bmodel compression\b", r"\bTensorRT\b",
    r"\bONNX\b", r"\bOpenVINO\b", r"\bNCNN\b", r"\bTFLite\b",
    # NLP
    r"\bNLP\b", r"\bnatural language\b", r"\bsentiment\b", r"\bNER\b",
    r"\btext classification\b", r"\bmachine translation\b", r"\bsummariz",
    # Infra/Ops
    r"\bMLOps\b", r"\bLLMOps\b", r"\bvector database\b", r"\bembedding",
    r"\bchromadb\b", r"\bpinecone\b", r"\bweaviate\b", r"\bfaiss\b",
    # Robotics / Autonomous
    r"\bautonomous\b", r"\brobotics\b", r"\breinforcement learning\b", r"\bRL\b",
    r"\bself.driving\b",
    # General
    r"\bneural network\b", r"\bdeep learning\b", r"\bmachine learning\b",
    r"\bartificial intelligence\b",
]

_KEYWORD_PATTERNS = [re.compile(kw, re.IGNORECASE) for kw in AI_KEYWORDS]


def heuristic_keyword_filter(text: str) -> KeywordFilterResult:
    """
    T0: Check if text contains at least one AI/ML keyword.
    Zero tokens spent. Returns DISCARD if no match found.
    """
    matched = [
        pat.pattern for pat in _KEYWORD_PATTERNS if pat.search(text)
    ]
    decision = FilterDecision.PASS if matched else FilterDecision.DISCARD
    return KeywordFilterResult(decision=decision, matched_keywords=matched[:10], token_spent=0)


# ─────────────────────────────────────────────────────────────────────────────
# T1 — LLM Relevance Scoring (GPT-4o-mini)
# ─────────────────────────────────────────────────────────────────────────────

_SCORING_SYSTEM_PROMPT = """You are a senior AI research analyst at Davision AI, a company specializing in:
- Computer Vision (object detection, segmentation, tracking, edge deployment)
- Large Language Models and RAG systems
- Edge AI and model optimization
- Multimodal AI systems

Evaluate the relevance of the provided article to Davision AI's focus areas.
Return ONLY a valid JSON object with this exact schema:
{
  "relevance_score": <float 0.0-10.0>,
  "primary_category": <one of: "Computer Vision"|"Natural Language Processing"|"Large Language Models"|"Edge AI"|"Robotics"|"Generative AI"|"MLOps"|"Multimodal AI"|"Other AI/ML">,
  "reasoning": <one sentence explaining the score>
}

Scoring guide:
9-10: Directly applicable to Davision AI products, breakthrough results
7-8:  Highly relevant, strong applicability
5-6:  Relevant but general/academic
3-4:  Tangentially related to AI/ML
1-2:  Minimal AI relevance
0:    Not related to AI at all"""


async def score_relevance(
    client: AsyncOpenAI,
    item: ScoutOutput,
    settings,
) -> ScoringResult:
    """T1: Score article relevance using GPT-4o-mini."""
    content_preview = item.raw_content[:1500]  # Cap to save tokens
    user_message = f"Title: {item.title}\n\nContent:\n{content_preview}"

    response = await client.chat.completions.create(
        model=settings.openai_scoring_model,
        messages=[
            {"role": "system", "content": _SCORING_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.1,
        max_tokens=200,
        response_format={"type": "json_object"},
    )

    raw_json = response.choices[0].message.content or "{}"
    data = json.loads(raw_json)

    # Map category string to enum (with fallback)
    try:
        category = PrimaryCategory(data.get("primary_category", "Other AI/ML"))
    except ValueError:
        category = PrimaryCategory.OTHER

    usage = response.usage
    total_tokens = usage.total_tokens if usage else 0

    return ScoringResult(
        relevance_score=float(data.get("relevance_score", 0.0)),
        primary_category=category,
        reasoning=data.get("reasoning", ""),
        token_spent=total_tokens,
    )


# ─────────────────────────────────────────────────────────────────────────────
# T2 — Turkish Executive Summary (GPT-4o-mini)
# ─────────────────────────────────────────────────────────────────────────────

_SUMMARY_SYSTEM_PROMPT = """Sen Davision AI'nın kıdemli AI araştırma analistisin.
Verilen makaleyi analiz et ve Davision AI'nın perspektifinden 3 maddelik Türkçe yönetici özeti oluştur.

KURALLAR:
- Her madde maksimum 150 karakter olmalı
- Davision AI'nın iş alanlarıyla (Bilgisayarlı Görü, LLM, Edge AI) bağlantı kur
- Teknik içgörü sağla, jargon kullan ama anlaşılır ol
- Varsa somut metrikleri (hız, doğruluk, boyut) belirt

Yanıtı YALNIZCA şu JSON formatında ver:
{
  "bullets": ["madde1", "madde2", "madde3"],
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}"""


async def generate_summary(
    client: AsyncOpenAI,
    item: ScoutOutput,
    scoring: ScoringResult,
    settings,
) -> SummaryResult:
    """T2: Generate Turkish 3-bullet executive summary."""
    content_preview = item.raw_content[:2000]
    user_message = (
        f"Makale Başlığı: {item.title}\n"
        f"Kategori: {scoring.primary_category.value}\n"
        f"İçerik:\n{content_preview}"
    )

    response = await client.chat.completions.create(
        model=settings.openai_summary_model,
        messages=[
            {"role": "system", "content": _SUMMARY_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.3,
        max_tokens=400,
        response_format={"type": "json_object"},
    )

    raw_json = response.choices[0].message.content or "{}"
    data = json.loads(raw_json)

    bullets = data.get("bullets", [])
    tags = data.get("tags", [])

    # Ensure exactly 3 bullets
    if len(bullets) < 3:
        bullets.extend(["İçerik analiz edilemedi."] * (3 - len(bullets)))
    bullets = bullets[:3]

    usage = response.usage
    total_tokens = usage.total_tokens if usage else 0

    return SummaryResult(
        bullets=bullets,
        tags=[str(t) for t in tags[:8]],
        token_spent=total_tokens,
    )


# ─────────────────────────────────────────────────────────────────────────────
# T3 — Vector Embedding (text-embedding-3-small)
# ─────────────────────────────────────────────────────────────────────────────

async def generate_embedding(
    client: AsyncOpenAI,
    text: str,
    settings,
) -> tuple[list[float], int]:
    """T3: Generate text embedding for ChromaDB storage."""
    # Embed title + first 500 chars of content for efficiency
    text_to_embed = text[:1500]
    response = await client.embeddings.create(
        model=settings.openai_embedding_model,
        input=text_to_embed,
    )
    embedding = response.data[0].embedding
    tokens = response.usage.total_tokens if response.usage else 0
    return embedding, tokens


# ─────────────────────────────────────────────────────────────────────────────
# DB Persistence Helpers
# ─────────────────────────────────────────────────────────────────────────────

async def _get_source_id(session: AsyncSession, source_name: SourceName) -> int:
    """Resolve source name to DB source_id."""
    result = await session.execute(
        select(Source.id).where(Source.name == source_name.value)
    )
    row = result.scalar_one_or_none()
    if row is None:
        raise ValueError(f"Source '{source_name.value}' not found in DB. Run migrations first.")
    return row


async def _persist_article(
    session: AsyncSession,
    item: ScoutOutput,
    output: AnalyzerOutput,
) -> int:
    """Insert article into PostgreSQL, return article ID."""
    import hashlib
    content_hash = hashlib.sha256(item.raw_content.encode()).hexdigest()
    source_id = await _get_source_id(session, item.source_name)

    article = Article(
        source_id=source_id,
        url=item.url,
        title=item.title,
        author=item.author,
        published_at=item.published_at,
        raw_content=item.raw_content,
        content_hash=content_hash,
        relevance_score=output.relevance_score,
        primary_category=output.primary_category.value if output.primary_category else None,
        tags=output.tags or [],
        summary_bullets=output.summary_bullets or [],
        token_spent=output.token_spent,
        chroma_doc_id=output.chroma_doc_id,
    )
    session.add(article)
    await session.flush()  # Get the ID without committing
    return article.id


async def _log_tokens(
    session: AsyncSession,
    article_id: int,
    model: str,
    operation: str,
    tokens: int,
) -> None:
    """Log token usage to token_logs table."""
    # Approximate cost calculation (USD)
    cost_per_1k = {
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "text-embedding-3-small": {"input": 0.00002, "output": 0.0},
    }
    base = cost_per_1k.get(model, {})
    cost = (tokens / 1000) * base.get("input", 0.0001)

    log = TokenLog(
        article_id=article_id,
        model=model,
        operation=operation,
        total_tokens=tokens,
        cost_usd=cost,
    )
    session.add(log)


# ─────────────────────────────────────────────────────────────────────────────
# Main Analyzer Entry Point
# ─────────────────────────────────────────────────────────────────────────────

async def analyze_item(
    client: AsyncOpenAI,
    item: ScoutOutput,
    settings,
) -> AnalyzerOutput:
    """
    Run the full 4-tier analysis pipeline for a single ScoutOutput item.

    Returns an AnalyzerOutput with relevance score, Turkish summary,
    tags, and chroma_doc_id (if embedded).
    """
    total_tokens = 0

    # ── T0: Heuristic keyword filter ─────────────────────────────────────────
    filter_result = heuristic_keyword_filter(
        f"{item.title} {item.raw_content}"
    )
    if filter_result.decision == FilterDecision.DISCARD:
        logger.debug(
            "analyzer.t0_discard",
            url=item.url,
            title=item.title[:60],
        )
        return AnalyzerOutput(
            source_name=item.source_name,
            url=item.url,
            title=item.title,
            author=item.author,
            published_at=item.published_at,
            relevance_score=0.0,
            primary_category=PrimaryCategory.OTHER,
            filter_decision=FilterDecision.DISCARD,
            token_spent=0,
        )

    # ── T1: LLM Relevance Scoring ─────────────────────────────────────────────
    scoring = await score_relevance(client, item, settings)
    total_tokens += scoring.token_spent
    logger.info(
        "analyzer.t1_scored",
        url=item.url,
        score=scoring.relevance_score,
        category=scoring.primary_category.value,
        tokens=scoring.token_spent,
    )

    # If score is below summary threshold, save raw entry and skip T2/T3
    if scoring.relevance_score < settings.relevance_threshold_summary:
        async with get_session() as session:
            output = AnalyzerOutput(
                source_name=item.source_name,
                url=item.url,
                title=item.title,
                author=item.author,
                published_at=item.published_at,
                relevance_score=scoring.relevance_score,
                primary_category=scoring.primary_category,
                filter_decision=FilterDecision.PASS,
                token_spent=total_tokens,
            )
            article_id = await _persist_article(session, item, output)
            await _log_tokens(
                session, article_id,
                settings.openai_scoring_model, "scoring", scoring.token_spent
            )
            output.article_id = article_id
        return output

    # ── T2: Turkish Executive Summary ─────────────────────────────────────────
    summary = await generate_summary(client, item, scoring, settings)
    total_tokens += summary.token_spent
    logger.info(
        "analyzer.t2_summary",
        url=item.url,
        tokens=summary.token_spent,
    )

    # ── T3: Vector Embedding ──────────────────────────────────────────────────
    embed_text = f"{item.title}\n{item.raw_content[:1000]}"
    embedding, embed_tokens = await generate_embedding(client, embed_text, settings)
    total_tokens += embed_tokens
    chroma_doc_id = f"article_{uuid.uuid4().hex[:16]}"

    output = AnalyzerOutput(
        source_name=item.source_name,
        url=item.url,
        title=item.title,
        author=item.author,
        published_at=item.published_at,
        relevance_score=scoring.relevance_score,
        primary_category=scoring.primary_category,
        tags=summary.tags,
        summary_bullets=summary.bullets,
        filter_decision=FilterDecision.PASS,
        token_spent=total_tokens,
        chroma_doc_id=chroma_doc_id,
    )

    # ── Persist to PostgreSQL ─────────────────────────────────────────────────
    async with get_session() as session:
        article_id = await _persist_article(session, item, output)
        output.article_id = article_id

        await _log_tokens(
            session, article_id,
            settings.openai_scoring_model, "scoring", scoring.token_spent
        )
        await _log_tokens(
            session, article_id,
            settings.openai_summary_model, "summary", summary.token_spent
        )
        await _log_tokens(
            session, article_id,
            settings.openai_embedding_model, "embedding", embed_tokens
        )

    # ── Store vector in ChromaDB ──────────────────────────────────────────────
    upsert_article_vector(
        doc_id=chroma_doc_id,
        embedding=embedding,
        document=embed_text,
        metadata={
            "article_id": str(article_id),
            "url": item.url,
            "title": item.title,
            "source": item.source_name.value,
            "category": scoring.primary_category.value,
            "relevance_score": scoring.relevance_score,
        },
    )

    logger.info(
        "analyzer.complete",
        article_id=article_id,
        score=scoring.relevance_score,
        total_tokens=total_tokens,
        chroma_doc_id=chroma_doc_id,
    )
    return output


async def run_analyzer(
    items: list[ScoutOutput],
    concurrency: int = 5,
) -> list[AnalyzerOutput]:
    """
    Analyze all Scout items with controlled concurrency.

    Args:
        items: List of ScoutOutput from the Scout Agent.
        concurrency: Max concurrent LLM calls (rate-limit protection).

    Returns:
        List of AnalyzerOutput with scores, summaries, and DB IDs.
    """
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    semaphore = asyncio.Semaphore(concurrency)

    async def analyze_with_semaphore(item: ScoutOutput) -> AnalyzerOutput | None:
        async with semaphore:
            try:
                return await analyze_item(client, item, settings)
            except Exception as exc:
                logger.error(
                    "analyzer.item_failed",
                    url=item.url,
                    error=str(exc),
                )
                return None

    tasks = [analyze_with_semaphore(item) for item in items]
    results = await asyncio.gather(*tasks)

    outputs = [r for r in results if r is not None]
    total_tokens = sum(o.token_spent for o in outputs)
    logger.info(
        "analyzer.run_complete",
        input=len(items),
        output=len(outputs),
        total_tokens=total_tokens,
    )
    return outputs
