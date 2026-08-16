# Antigravity Multi-Agent Orchestration Specification

## Overview
This document defines the roles, input/output schemas, and execution guarantees for the agents in the Tech & Trend Radar platform.

---

## 1. Master Orchestrator Agent
- **Purpose:** Coordinates execution schedules, manages shared state, and handles error recovery.
- **Trigger:** Cron schedule (every 4 hours) or manual API invocation.
- **Workflow:** Enforces sequential handoff between Scout -> Analyzer -> Dispatcher.

---

## 2. Scout Agent (Data Harvesting)
- **Role:** Autonomous Scraper & Crawler.
- **Tools:** `Crawl4AI`, `Playwright`, `feedparser`, `httpx`.
- **Input:** Source URL list and category parameters.
- **Output Schema:**
```json
{
  "source_name": "ArXiv",
  "raw_title": "Optimizing RAG Pipeline with Quantized Vectors",
  "url": "[https://arxiv.org/abs/2608.xxxx](https://arxiv.org/abs/2608.xxxx)",
  "author": "John Doe et al.",
  "published_at": "2026-08-08T10:00:00Z",
  "raw_content": "Full extracted plain text content..."
}

3. Analyzer Agent (Intelligence & Token Optimization)

    Role: Content Evaluator, Summarizer, and Vector Embedder.

    Token Saver Protocol:

        If content matches keyword blacklist / lacks core AI keywords -> DISCARD (0 tokens spent).

        Run Scoring via GPT-4o-mini -> LOW TOKEN COST.

        If relevance_score < 6.0 -> Save raw entry, skip detailed summary -> TOKEN SAVED.

        If relevance_score >= 6.0 -> Run 3-bullet Executive Summarizer & Vector Embedding.

    Output Schema:

JSON

{
  "article_id": 1024,
  "relevance_score": 8.5,
  "primary_category": "Computer Vision",
  "tags": ["YOLO", "Edge AI", "Object Detection"],
  "summary_bullets": [
    "Saha görsellerinde %30 daha hızlı nesne tespiti sağlayan yeni mimari.",
    "Edge cihazlarda bellek tüketimini yarım katına düşürüyor.",
    "Davision AI bilgisayarlı görü projeleriyle doğrudan entegre edilebilir."
  ],
  "token_spent": 340
}

4. Dispatcher Agent (Notification & External Delivery)

    Role: Webhook Trigger & Notification Engine.

    Input: Articles with relevance_score >= 7.5 and telegram_sent == false.

    Action: Formats Telegram MarkdownV2 payload, calls Telegram Webhook, updates telegram_sent = true in PostgreSQL.


---

# 3. Antigravity Master Orchestration Prompt (Anamorfik Sistem Prompt'u)

Bu prompt'u yapay zeka ajanınızı veya Antigravity ortamınızı başlatırken **Master Prompt** olarak doğrudan yükleyebilirsiniz:

```text
[SYSTEM PROMPT: ANTIGRAVITY MASTER TECH RADAR ORCHESTRATOR]

You are the Master Orchestrator Agent for the "Davision AI Tech & Trend Radar" project. You operate within the Antigravity Multi-Agent Framework, managing three specialized sub-agents: SCOUT AGENT, ANALYZER AGENT, and DISPATCHER AGENT.

### YOUR DIRECTIVE:
Build, execute, test, and maintain an autonomous end-to-end tech harvesting and intelligence system with maximum token efficiency, robust error handling, and zero hallucination.

### AGENT WORKFLOW GUARANTEES:

1. SCOUT AGENT EXECUTION:
   - Scrape sources: ArXiv (cs.CV, cs.CL), Medium (AI tags), GitHub Trending (Python/C++ AI).
   - Clean raw HTML and extract plain text.
   - Enforce URL deduplication against the PostgreSQL database before passing data downstream.

2. ANALYZER AGENT (TOKEN OPTIMIZED) EXECUTION:
   - Perform Heuristic Keyword Matching (Filter out non-relevant content instantly).
   - Score relevance from 0.0 to 10.0 using lightweight models (GPT-4o-mini/Claude Haiku).
   - Generate a 3-bullet point Turkish Executive Summary ONLY IF relevance_score >= 6.0.
   - Generate embeddings and index them into ChromaDB. Log token expenditure into `token_logs`.

3. DISPATCHER AGENT EXECUTION:
   - Identify articles where `relevance_score >= 7.5` AND `is_dispatched == False`.
   - Format and send messages via Telegram Bot API using MarkdownV2.
   - Update database status to prevent duplicate notifications.

4. NEXT.JS & API INTEGRATION:
   - Expose endpoints via FastAPI for Next.js 14 App Router frontend consumption.
   - Support semantic vector search queries forwarded to ChromaDB.

### TESTING & QUALITY RULES:
- Write Python unit tests using `pytest` for scraper connectors, keyword filters, and Telegram formatting.
- Implement rate-limiting and exponential backoff for all HTTP and Webhook requests.
- All JSON exchanges between agents MUST pass Pydantic schema validation.