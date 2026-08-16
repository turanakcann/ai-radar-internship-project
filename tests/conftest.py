"""
tests/conftest.py — Shared pytest fixtures for all test modules.

Provides:
- In-memory SQLite DB session for unit tests
- Mock settings with safe defaults (no real API keys required)
- Sample ScoutOutput / AnalyzerOutput factory fixtures
"""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from core.schemas import (
    AnalyzerOutput,
    FilterDecision,
    PrimaryCategory,
    ScoutOutput,
    SourceName,
)


# ─────────────────────────────────────────────────────────────────────────────
# Settings override — safe for CI (no real API keys)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    """Patch get_settings() to return safe test defaults."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test_radar")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-0000000000000000000000000000000000000000000000000")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456789:AABBccDDeeFFggHH")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-1001234567890")
    monkeypatch.setenv("CHROMADB_PATH", "/tmp/test_chromadb")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")


# ─────────────────────────────────────────────────────────────────────────────
# Sample data factories
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_arxiv_item() -> ScoutOutput:
    """A realistic ArXiv ScoutOutput for testing."""
    return ScoutOutput(
        source_name=SourceName.ARXIV,
        url="https://arxiv.org/abs/2608.12345",
        title="YOLOv12: Real-Time Object Detection with Edge AI Optimization",
        author="Jane Smith, John Doe et al.",
        published_at=datetime(2026, 8, 8, 10, 0, tzinfo=timezone.utc),
        raw_content=(
            "We propose YOLOv12, a novel architecture for real-time object detection "
            "optimized for edge devices using quantization and neural network pruning. "
            "Our method achieves 30% faster inference with 50% less memory consumption "
            "compared to YOLOv11 while maintaining competitive accuracy on standard "
            "computer vision benchmarks. The model supports ONNX and TensorRT export."
        ),
    )


@pytest.fixture
def sample_medium_item() -> ScoutOutput:
    """A realistic Medium ScoutOutput for testing."""
    return ScoutOutput(
        source_name=SourceName.MEDIUM,
        url="https://medium.com/@author/building-production-rag-systems-2026-abc123",
        title="Building Production RAG Systems in 2026: A Complete Guide",
        author="AI Engineer",
        published_at=datetime(2026, 8, 7, 14, 0, tzinfo=timezone.utc),
        raw_content=(
            "Retrieval-Augmented Generation (RAG) has become the de-facto pattern for "
            "building LLM-powered applications. In this guide, we cover vector database "
            "selection (ChromaDB vs Pinecone vs Weaviate), embedding model choices, "
            "chunking strategies, and re-ranking approaches for production RAG pipelines. "
            "We also discuss fine-tuning vs prompt engineering trade-offs."
        ),
    )


@pytest.fixture
def sample_github_item() -> ScoutOutput:
    """A realistic GitHub ScoutOutput for testing."""
    return ScoutOutput(
        source_name=SourceName.GITHUB,
        url="https://github.com/ultralytics/ultralytics",
        title="[GitHub Trending] ultralytics / ultralytics",
        author="Glenn Jocher",
        published_at=datetime(2026, 8, 8, tzinfo=timezone.utc),
        raw_content=(
            "Repository: ultralytics / ultralytics\n"
            "Language: Python\n"
            "Description: Ultralytics YOLO11 for object detection, "
            "segmentation, and pose estimation with Edge AI optimization.\n"
            "Total Stars: 45,231\n"
            "Stars Today: 234\n"
            "Trending Period: daily\n"
            "URL: https://github.com/ultralytics/ultralytics"
        ),
    )


@pytest.fixture
def sample_non_ai_item() -> ScoutOutput:
    """A non-AI item that should be discarded at T0."""
    return ScoutOutput(
        source_name=SourceName.MEDIUM,
        url="https://medium.com/@cook/best-pasta-recipe-2026",
        title="The Ultimate Guide to Homemade Pasta in 2026",
        author="Chef Mario",
        published_at=datetime(2026, 8, 8, tzinfo=timezone.utc),
        raw_content=(
            "Learn how to make authentic Italian pasta from scratch. "
            "This guide covers flour selection, egg ratios, and kneading techniques "
            "for perfect homemade pasta every time. Includes recipes for tagliatelle, "
            "pappardelle, and lasagna sheets."
        ),
    )


@pytest.fixture
def sample_analyzer_output() -> AnalyzerOutput:
    """A high-scoring AnalyzerOutput ready for dispatch."""
    return AnalyzerOutput(
        article_id=1024,
        source_name=SourceName.ARXIV,
        url="https://arxiv.org/abs/2608.12345",
        title="YOLOv12: Real-Time Object Detection with Edge AI Optimization",
        author="Jane Smith et al.",
        published_at=datetime(2026, 8, 8, 10, 0, tzinfo=timezone.utc),
        relevance_score=8.5,
        primary_category=PrimaryCategory.COMPUTER_VISION,
        tags=["YOLO", "Edge AI", "Object Detection", "Quantization", "TensorRT"],
        summary_bullets=[
            "Saha görsellerinde %30 daha hızlı nesne tespiti sağlayan yeni YOLO mimarisi.",
            "Edge cihazlarda bellek tüketimini yarıya düşüren kuantizasyon optimizasyonu.",
            "Davision AI'nın bilgisayarlı görü projeleriyle doğrudan entegre edilebilir.",
        ],
        filter_decision=FilterDecision.PASS,
        token_spent=520,
        chroma_doc_id="article_abc123def456",
    )
