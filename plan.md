# Antigravity Multi-Agent Tech & Trend Radar - Master Implementation Plan

## Executive Summary
An autonomous, multi-agent intelligence platform built on Antigravity Agentic Framework. The platform features a **Next.js 14+ App Router Frontend**, **FastAPI + PostgreSQL + ChromaDB Backend**, **Telegram Dispatcher Webhook**, and a **Token Optimization Pipeline**.

---

## 1. System Architecture & Topology

                           ┌─────────────────────────────────────────┐
                           │    Antigravity Master Orchestrator      │
                           └────────────────────┬────────────────────┘
                                                │
     ┌──────────────────────────────────────────┼──────────────────────────────────────────┐
     ▼                                          ▼                                          ▼

┌──────────────────┐                      ┌──────────────────┐                      ┌──────────────────┐
│  Scout Agent     │                      │  Analyzer Agent  │                      │ Dispatcher Agent │
│ (Crawl4AI/Play)  │ ──(Raw Text)──>      │ (Token Optimized)│ ──(JSON & Vectors)──> │ (Telegram Bot &  │
└──────────────────┘                      └──────────────────┘                      │  Next.js API)    │
└──────────────────┘
│
▼
┌──────────────────┐
│ Next.js 14 Web UI│
│ (Shadcn/Recharts)│
└──────────────────┘


---

## 2. Phase Breakdown & Tasks

### Phase 1: Environment Setup & Infrastructure (Day 1-2)
- [ ] Initialize Python 3.11+ virtual environment and Poetry/Pipenv.
- [ ] Set up Docker Compose environment: PostgreSQL, ChromaDB, Redis.
- [ ] Create database schemas (`sources`, `articles`, `token_logs`, `telegram_dispatches`).
- [ ] Initialize Next.js 14 App Router with Tailwind CSS and Shadcn UI.

### Phase 2: Scout Agent & Ingestion Pipeline (Day 3-5)
- [ ] Implement `Scout Agent` using `Crawl4AI` and `Playwright`.
- [ ] Develop individual source connectors:
  - [ ] ArXiv API connector (`cs.CV`, `cs.CL`).
  - [ ] Medium RSS and Tag Scraper (AI/ML tags).
  - [ ] GitHub Trending Repositories Scraper (Python/C++ AI repos).
- [ ] Add URL deduplication and raw text cleaning layer.

### Phase 3: Analyzer Agent & Token Optimization (Day 6-9)
- [ ] Build **Token Savings Pipeline**:
  - [ ] Step 1: URL & Content Hash Deduplication.
  - [ ] Step 2: Heuristic Keyword Filter (Computer Vision, RAG, LLM, Edge AI).
  - [ ] Step 3: Model Tiering (GPT-4o-mini / Haiku for scoring; Full LLM only if Score >= 6.0).
- [ ] Implement structured JSON output using Pydantic / Instructor.
- [ ] Generate 3-bullet point Executive Summaries in Turkish/English.
- [ ] Generate and store embeddings in `ChromaDB`.

### Phase 4: Dispatcher Agent & Telegram Webhook (Day 10-11)
- [ ] Implement `Dispatcher Agent` with Telegram Bot API integration.
- [ ] Format high-priority alerts (`Score >= 7.5`) with Telegram MarkdownV2.
- [ ] Set up state tracking in PostgreSQL to prevent duplicate notifications.

### Phase 5: FastAPI Backend & Next.js 14 UI (Day 12-16)
- [ ] Develop FastAPI REST endpoints (`/api/articles`, `/api/search`, `/api/stats`).
- [ ] Build Next.js 14 Dashboard:
  - [ ] Feed view with Score Badges & Category filters.
  - [ ] Semantic Vector Search Bar powered by ChromaDB.
  - [ ] Analytics Page with Recharts (Token usage, daily ingestion trends).

### Phase 6: Automated Testing & Deployment (Day 17-20)
- [ ] Write Unit Tests for Scrapers, Token Filter, and Telegram Webhook.
- [ ] Integration tests for Agent handoffs (Scout -> Analyzer -> Dispatcher).
- [ ] End-to-End orchestration using `APScheduler`.
- [ ] Final Docker deployment & documentation.