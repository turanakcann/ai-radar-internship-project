"""
tests/test_analyzer.py — Unit tests for the Analyzer Agent.

Tests the T0 keyword filter, scoring result validation,
summary structure, and AnalyzerOutput schema.
"""
from __future__ import annotations

import pytest

from agents.analyzer_agent import heuristic_keyword_filter
from core.schemas import (
    AnalyzerOutput,
    FilterDecision,
    PrimaryCategory,
    ScoutOutput,
    SourceName,
    SummaryResult,
)
from datetime import datetime, timezone


# ─────────────────────────────────────────────────────────────────────────────
# T0 — Keyword Filter Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestKeywordFilter:
    """T0 heuristic keyword filter must match known AI terms and reject unrelated content."""

    @pytest.mark.parametrize("text,expected_decision", [
        # Should PASS
        ("YOLO object detection for edge AI deployment", FilterDecision.PASS),
        ("Large Language Model fine-tuning with RAG pipeline", FilterDecision.PASS),
        ("Computer vision transformer ViT for medical imaging", FilterDecision.PASS),
        ("Semantic segmentation with diffusion model", FilterDecision.PASS),
        ("Quantization and pruning for mobile neural network", FilterDecision.PASS),
        ("Multimodal vision-language model", FilterDecision.PASS),
        ("Reinforcement learning autonomous robotics", FilterDecision.PASS),
        # Should DISCARD
        ("New recipe for chocolate cake", FilterDecision.DISCARD),
        ("Stock market analysis Q3 2026", FilterDecision.DISCARD),
        ("Football match results weekend", FilterDecision.DISCARD),
        ("Travel guide to Istanbul", FilterDecision.DISCARD),
    ])
    def test_filter_decision(self, text: str, expected_decision: FilterDecision):
        result = heuristic_keyword_filter(text)
        assert result.decision == expected_decision

    def test_filter_returns_matched_keywords(self):
        result = heuristic_keyword_filter("YOLO object detection")
        assert result.decision == FilterDecision.PASS
        assert len(result.matched_keywords) > 0

    def test_filter_zero_tokens(self):
        result = heuristic_keyword_filter("anything")
        assert result.token_spent == 0

    def test_filter_case_insensitive(self):
        result = heuristic_keyword_filter("deep learning for COMPUTER VISION")
        assert result.decision == FilterDecision.PASS

    def test_filter_partial_match(self):
        # 'quantiz' should match 'quantization', 'quantized', etc.
        result = heuristic_keyword_filter("Model quantization for deployment")
        assert result.decision == FilterDecision.PASS


# ─────────────────────────────────────────────────────────────────────────────
# SummaryResult Schema Validation
# ─────────────────────────────────────────────────────────────────────────────

class TestSummaryResult:
    def test_valid_three_bullets(self):
        summary = SummaryResult(
            bullets=["Bullet 1", "Bullet 2", "Bullet 3"],
            tags=["YOLO", "Edge AI"],
            token_spent=350,
        )
        assert len(summary.bullets) == 3

    def test_rejects_two_bullets(self):
        with pytest.raises(Exception):
            SummaryResult(
                bullets=["Bullet 1", "Bullet 2"],
                tags=[],
                token_spent=0,
            )

    def test_rejects_four_bullets(self):
        with pytest.raises(Exception):
            SummaryResult(
                bullets=["B1", "B2", "B3", "B4"],
                tags=[],
                token_spent=0,
            )


# ─────────────────────────────────────────────────────────────────────────────
# AnalyzerOutput Schema
# ─────────────────────────────────────────────────────────────────────────────

class TestAnalyzerOutput:
    def test_valid_output(self):
        output = AnalyzerOutput(
            source_name=SourceName.ARXIV,
            url="https://arxiv.org/abs/2608.12345",
            title="YOLO Edge Optimization",
            relevance_score=8.5,
            primary_category=PrimaryCategory.COMPUTER_VISION,
            tags=["YOLO", "Edge AI", "Object Detection"],
            summary_bullets=["Bullet 1", "Bullet 2", "Bullet 3"],
            filter_decision=FilterDecision.PASS,
            token_spent=500,
        )
        assert output.relevance_score == 8.5
        assert output.primary_category == PrimaryCategory.COMPUTER_VISION

    def test_score_boundaries(self):
        with pytest.raises(Exception):
            AnalyzerOutput(
                source_name=SourceName.ARXIV,
                url="https://arxiv.org/abs/test",
                title="Test",
                relevance_score=10.5,  # Over limit
                primary_category=PrimaryCategory.OTHER,
                filter_decision=FilterDecision.PASS,
            )
