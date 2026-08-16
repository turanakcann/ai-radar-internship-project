"""api/routes/stats.py — Pipeline statistics and analytics endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import cast, func, select, text, Float
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.models import Article, Source, TokenLog
from core.schemas import PipelineStats

router = APIRouter()


@router.get("/stats", response_model=PipelineStats)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """
    Return pipeline analytics:
    - Total articles ingested
    - Breakdown by source and category
    - Token spend and cost
    - Dispatch rate
    - Daily ingestion trend (last 14 days)
    """
    try:
        total_result = await db.execute(select(func.count(Article.id)))
        total_articles = total_result.scalar() or 0

        by_source_result = await db.execute(
            select(Source.name, func.count(Article.id))
            .join(Article, Article.source_id == Source.id)
            .group_by(Source.name)
        )
        articles_by_source = {row[0]: row[1] for row in by_source_result.all()}

        by_cat_result = await db.execute(
            select(Article.primary_category, func.count(Article.id))
            .where(Article.primary_category.isnot(None))
            .group_by(Article.primary_category)
            .order_by(func.count(Article.id).desc())
        )
        articles_by_category = {
            row[0]: row[1] for row in by_cat_result.all()
        }

        token_result = await db.execute(
            select(
                func.sum(TokenLog.total_tokens),
                func.sum(TokenLog.cost_usd),
            )
        )
        token_row = token_result.one()
        total_tokens = int(token_row[0] or 0)
        total_cost = float(token_row[1] or 0.0)

        dispatched_result = await db.execute(
            select(func.count(Article.id)).where(Article.is_dispatched.is_(True))
        )
        dispatched_count = dispatched_result.scalar() or 0

        daily_result = await db.execute(
            text("""
            SELECT
                date_trunc('day', created_at AT TIME ZONE 'UTC')::date AS day,
                COUNT(*) AS count,
                ROUND(AVG(relevance_score)::numeric, 2) AS avg_score
            FROM articles
            WHERE created_at >= NOW() - INTERVAL '14 days'
            GROUP BY 1
            ORDER BY 1
            """)
        )
        daily_ingestion = [
            {"date": str(row[0]), "count": int(row[1]), "avg_score": float(row[2] or 0)}
            for row in daily_result.all()
        ]

        return PipelineStats(
            total_articles=total_articles,
            articles_by_source=articles_by_source,
            articles_by_category=articles_by_category,
            total_tokens_spent=total_tokens,
            total_cost_usd=total_cost,
            dispatched_count=dispatched_count,
            daily_ingestion=daily_ingestion,
        )
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Analytics unavailable due to database schema or connection issues.",
        ) from exc
