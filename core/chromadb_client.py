"""
core/chromadb_client.py — ChromaDB wrapper for vector storage and semantic search.

Supports both:
  - Embedded persistent mode (local directory, default for dev)
  - HTTP client mode (Docker service, for production)
"""
from __future__ import annotations

import os

# Disable ChromaDB telemetry before the package is imported.
# In chromadb 0.5.x the posthog client is initialised as a module-level
# singleton, so the Settings flag only helps if the env var is already set.
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
os.environ.setdefault("CHROMA_TELEMETRY", "False")

import chromadb
from chromadb import Collection
from chromadb.config import Settings as ChromaSettings
from functools import lru_cache
from typing import Any

from core.config import get_settings


@lru_cache(maxsize=1)
def get_chroma_client() -> chromadb.ClientAPI:
    """Return a cached ChromaDB client (embedded or HTTP)."""
    settings = get_settings()

    if settings.chromadb_use_http:
        return chromadb.HttpClient(
            host=settings.chromadb_host,
            port=settings.chromadb_port,
            settings=ChromaSettings(anonymized_telemetry=False),
        )

    return chromadb.PersistentClient(
        path=settings.chromadb_path,
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def get_collection() -> Collection:
    """Get or create the main article collection."""
    client = get_chroma_client()
    settings = get_settings()
    return client.get_or_create_collection(
        name=settings.chromadb_collection,
        metadata={"hnsw:space": "cosine"},
    )


def upsert_article_vector(
    doc_id: str,
    embedding: list[float],
    document: str,
    metadata: dict[str, Any],
) -> None:
    """Upsert an article embedding into ChromaDB."""
    collection = get_collection()
    collection.upsert(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[document],
        metadatas=[metadata],
    )


def query_similar(
    query_embedding: list[float],
    top_k: int = 10,
    where: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Perform a semantic similarity search.

    Returns ChromaDB query results dict with keys:
    ids, distances, documents, metadatas
    """
    collection = get_collection()
    kwargs: dict[str, Any] = {
        "query_embeddings": [query_embedding],
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"],
    }
    if where:
        kwargs["where"] = where
    return collection.query(**kwargs)
