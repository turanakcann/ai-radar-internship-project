"""api/routes/articles.py — Articles feed endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.models import Article, Source
from core.schemas import ArticleResponse

router = APIRouter()


@router.get("/articles", response_model=list[ArticleResponse])
async def list_articles(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    source: Optional[str] = Query(default=None, description="Filter by source name (arxiv|medium|github)"),
    category: Optional[str] = Query(default=None, description="Filter by primary_category"),
    min_score: Optional[float] = Query(default=None, ge=0.0, le=10.0),
    dispatched: Optional[bool] = Query(default=None, description="Filter by Telegram dispatch status"),
    date_from: Optional[datetime] = Query(default=None, description="ISO datetime — published_at start"),
    date_to: Optional[datetime] = Query(default=None, description="ISO datetime — published_at end"),
    db: AsyncSession = Depends(get_db),
):
    """
    List articles with optional filtering and pagination.

    - **page**: Page number (1-indexed)
    - **page_size**: Items per page (max 100)
    - **source**: Filter by source (arxiv, medium, github)
    - **category**: Filter by AI category
    - **min_score**: Minimum relevance score
    - **dispatched**: Filter by Telegram dispatch status
    - **date_from** / **date_to**: Filter by published_at date range
    """
    # Single JOIN query — no N+1
    query = (
        select(Article, Source.name.label("source_name"))
        .join(Source, Article.source_id == Source.id, isouter=True)
        .order_by(
            Article.relevance_score.desc().nullslast(),
            Article.created_at.desc(),
        )
    )

    if source:
        query = query.where(Source.name == source.lower())

    if category:
        query = query.where(Article.primary_category.ilike(f"%{category}%"))

    if min_score is not None:
        query = query.where(Article.relevance_score >= min_score)

    if dispatched is not None:
        query = query.where(Article.is_dispatched == dispatched)

    if date_from is not None:
        query = query.where(Article.published_at >= date_from)

    if date_to is not None:
        query = query.where(Article.published_at <= date_to)

    # Pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    try:
        result = await db.execute(query)
        rows = result.all()
    except ProgrammingError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database schema unavailable. Please retry shortly.",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable due to database connectivity issues.",
        )

    return [
        ArticleResponse(
            id=a.id,
            source_name=source_name or "unknown",
            url=a.url,
            title=a.title,
            author=a.author,
            published_at=a.published_at,
            relevance_score=float(a.relevance_score) if a.relevance_score else None,
            primary_category=a.primary_category,
            tags=list(a.tags or []),
            summary_bullets=list(a.summary_bullets or []),
            is_dispatched=a.is_dispatched,
            created_at=a.created_at,
        )
        for a, source_name in rows
    ]


@router.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single article by ID with full detail."""
    result = await db.execute(
        select(Article, Source.name.label("source_name"))
        .join(Source, Article.source_id == Source.id, isouter=True)
        .where(Article.id == article_id)
    )
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Article not found")

    article, source_name = row

    return ArticleResponse(
        id=article.id,
        source_name=source_name or "unknown",
        url=article.url,
        title=article.title,
        author=article.author,
        published_at=article.published_at,
        relevance_score=float(article.relevance_score) if article.relevance_score else None,
        primary_category=article.primary_category,
        tags=list(article.tags or []),
        summary_bullets=list(article.summary_bullets or []),
        is_dispatched=article.is_dispatched,
        created_at=article.created_at,
    )

