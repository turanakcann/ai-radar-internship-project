"""api/routes/search.py — Semantic vector search endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.chromadb_client import query_similar
from core.config import get_settings
from core.database import get_db
from core.models import Article, Source
from core.schemas import ArticleResponse, SearchRequest, SearchResult

router = APIRouter()


async def _get_query_embedding(query_text: str) -> list[float]:
    """Generate embedding for a search query."""
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.embeddings.create(
        model=settings.openai_embedding_model,
        input=query_text[:500],
    )
    return response.data[0].embedding


@router.post("/search", response_model=list[SearchResult])
async def semantic_search(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Perform semantic vector similarity search over indexed articles.

    Queries ChromaDB with an embedding of the user's query, then
    fetches full article metadata from PostgreSQL.

    - **query**: Natural language search query (min 3 chars)
    - **top_k**: Number of results to return (max 50)
    - **min_score**: Minimum relevance_score filter
    """
    # Generate query embedding
    try:
        query_embedding = await _get_query_embedding(request.query)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Embedding service unavailable: {exc}",
        )

    # Query ChromaDB
    where_filter = None
    if request.min_score > 0:
        where_filter = {"relevance_score": {"$gte": request.min_score}}

    try:
        chroma_results = query_similar(
            query_embedding=query_embedding,
            top_k=request.top_k,
            where=where_filter,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Vector search failed: {exc}",
        )

    # Extract article IDs and distances from ChromaDB results
    ids = chroma_results.get("ids", [[]])[0]
    distances = chroma_results.get("distances", [[]])[0]
    metadatas = chroma_results.get("metadatas", [[]])[0]

    if not ids:
        return []

    # Fetch full article data from PostgreSQL
    article_ids = []
    id_to_distance: dict[int, float] = {}
    for chroma_id, distance, meta in zip(ids, distances, metadatas):
        article_id = int(meta.get("article_id", 0))
        if article_id:
            article_ids.append(article_id)
            id_to_distance[article_id] = distance

    result = await db.execute(
        select(Article, Source.name.label("source_name"))
        .join(Source, Article.source_id == Source.id)
        .where(Article.id.in_(article_ids))
    )
    rows = result.all()

    # Map and sort by similarity (lower distance = more similar)
    search_results = []
    for article, source_name in rows:
        similarity = 1.0 - id_to_distance.get(article.id, 1.0)  # cosine similarity
        search_results.append(
            SearchResult(
                article=ArticleResponse(
                    id=article.id,
                    source_name=source_name,
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
                ),
                similarity_score=round(similarity, 4),
            )
        )

    # Sort by similarity descending
    search_results.sort(key=lambda x: x.similarity_score, reverse=True)
    return search_results
