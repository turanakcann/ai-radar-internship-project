# 🚀 Davision AI Tech & Trend Radar

> Autonomous multi-agent intelligence platform for AI/ML research discovery.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green.svg)](https://fastapi.tiangolo.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5-orange.svg)](https://trychroma.com)

---

## Architecture

```
APScheduler (every 4h)
    │
    ├─► Scout Agent        (ArXiv · Medium · GitHub Trending)
    │       ↓ URL dedup against PostgreSQL
    │       ↓ Text cleaning
    │
    ├─► Analyzer Agent     (4-Tier Token Protocol)
    │       T0: Keyword filter     → 0 tokens
    │       T1: GPT-4o-mini score  → ~150 tokens
    │       T2: Turkish summary    → ~300 tokens (if score ≥ 6.0)
    │       T3: Embedding          → ~50 tokens  (if score ≥ 6.0)
    │       ↓ PostgreSQL + ChromaDB
    │
    └─► Dispatcher Agent   (Telegram MarkdownV2 alerts, score ≥ 7.5)
            ↓ mark is_dispatched = True

FastAPI REST API  ←→  Next.js 14 Dashboard
    /api/articles      Feed + filters
    /api/search        Semantic vector search
    /api/stats         Analytics & token spend
    /api/run           Manual pipeline trigger
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- OpenAI API key
- Telegram Bot Token + Chat ID

### 1. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 2. Start Infrastructure

```bash
docker compose up -d postgres chromadb redis
```

### 3. Install Python Dependencies

```bash
pip install poetry
poetry install
```

### 4. Start the Backend

```bash
# FastAPI Server
uvicorn api.main:app --reload --port 8000

# Scheduler (separate terminal)
python -m agents.orchestrator
```

### 5. Start the Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### Manual Pipeline Trigger

```bash
curl -X POST http://localhost:8000/api/run
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | PostgreSQL asyncpg URL |
| `OPENAI_API_KEY` | ✅ | OpenAI API key for scoring + embeddings |
| `TELEGRAM_BOT_TOKEN` | ✅ | Telegram Bot API token |
| `TELEGRAM_CHAT_ID` | ✅ | Target chat/channel ID |
| `ANTHROPIC_API_KEY` | ☐ | Fallback LLM (optional) |
| `SCHEDULE_INTERVAL_HOURS` | ☐ | Cron interval (default: 4) |
| `RELEVANCE_THRESHOLD_SUMMARY` | ☐ | Min score for Turkish summary (default: 6.0) |
| `RELEVANCE_THRESHOLD_DISPATCH` | ☐ | Min score for Telegram alert (default: 7.5) |

## Token Optimization

The Analyzer uses a strict 4-tier protocol to minimize API costs:

| Tier | Condition | Action | Token Cost |
|------|-----------|--------|-----------|
| T0 | No AI keywords in text | Discard immediately | **0** |
| T1 | Passes T0 | GPT-4o-mini relevance score | ~150 |
| T2 | Score ≥ 6.0 | Turkish 3-bullet summary | ~300 |
| T3 | Score ≥ 6.0 | text-embedding-3-small | ~50 |

## Running Tests

```bash
poetry run pytest tests/ -v --cov=. --cov-report=term-missing
```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/articles` | Paginated article feed with filters |
| GET | `/api/articles/{id}` | Single article detail |
| POST | `/api/search` | Semantic vector search |
| GET | `/api/stats` | Pipeline analytics |
| POST | `/api/run` | Trigger pipeline manually |
| GET | `/api/health` | Health check |

## Frontend Pages

| Page | URL | Description |
|------|-----|-------------|
| Feed | `/` | Article feed with source/category/score filters |
| Search | `/search` | Semantic vector search with similarity scores |
| Analytics | `/analytics` | Token spend, ingestion trends, category breakdown |

## Docker Deployment

```bash
docker compose up --build
```

Services:
- `postgres`: PostgreSQL 16 on port 5432
- `chromadb`: ChromaDB on port 8001
- `redis`: Redis 7 on port 6379
- `api`: FastAPI on port 8000
- `scheduler`: APScheduler orchestrator

---

Built with ❤️ by **Davision AI** — Autonomous Intelligence Platform
