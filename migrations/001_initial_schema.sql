-- ═══════════════════════════════════════════════════════════════════════════
-- Davision AI Tech & Trend Radar — Initial Database Schema
-- Migration 001
-- ═══════════════════════════════════════════════════════════════════════════

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- for LIKE/ILIKE index support

-- ── sources ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sources (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,   -- e.g. 'arxiv', 'medium', 'github'
    base_url    TEXT NOT NULL,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO sources (name, base_url) VALUES
    ('arxiv',  'https://arxiv.org'),
    ('medium', 'https://medium.com'),
    ('github', 'https://github.com/trending')
ON CONFLICT DO NOTHING;

-- ── articles ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS articles (
    id                  BIGSERIAL PRIMARY KEY,
    source_id           INTEGER NOT NULL REFERENCES sources(id),
    url                 TEXT NOT NULL UNIQUE,
    url_hash            CHAR(64) GENERATED ALWAYS AS (encode(sha256(url::bytea), 'hex')) STORED,
    title               TEXT NOT NULL,
    author              TEXT,
    published_at        TIMESTAMPTZ,
    raw_content         TEXT,
    content_hash        CHAR(64),              -- sha256 of raw_content for dedup
    -- Analyzer outputs
    relevance_score     NUMERIC(4,2),          -- 0.00 – 10.00
    primary_category    VARCHAR(100),          -- e.g. 'Computer Vision'
    tags                TEXT[],
    summary_bullets     TEXT[],                -- 3-bullet Turkish executive summary
    token_spent         INTEGER DEFAULT 0,
    -- Dispatcher state
    is_dispatched       BOOLEAN NOT NULL DEFAULT FALSE,
    dispatched_at       TIMESTAMPTZ,
    -- ChromaDB reference
    chroma_doc_id       TEXT,
    -- Lifecycle
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_articles_source_id       ON articles(source_id);
CREATE INDEX IF NOT EXISTS idx_articles_relevance_score ON articles(relevance_score DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_articles_is_dispatched   ON articles(is_dispatched) WHERE is_dispatched = FALSE;
CREATE INDEX IF NOT EXISTS idx_articles_published_at    ON articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_primary_category ON articles(primary_category);
CREATE INDEX IF NOT EXISTS idx_articles_url_hash        ON articles(url_hash);
-- Full-text search on title
CREATE INDEX IF NOT EXISTS idx_articles_title_trgm     ON articles USING gin(title gin_trgm_ops);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_articles_updated_at
    BEFORE UPDATE ON articles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ── token_logs ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS token_logs (
    id              BIGSERIAL PRIMARY KEY,
    article_id      BIGINT REFERENCES articles(id) ON DELETE CASCADE,
    model           VARCHAR(100) NOT NULL,
    operation       VARCHAR(50) NOT NULL,   -- 'scoring', 'summary', 'embedding'
    prompt_tokens   INTEGER NOT NULL DEFAULT 0,
    completion_tokens INTEGER NOT NULL DEFAULT 0,
    total_tokens    INTEGER NOT NULL DEFAULT 0,
    cost_usd        NUMERIC(12,8),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_token_logs_article_id ON token_logs(article_id);
CREATE INDEX IF NOT EXISTS idx_token_logs_created_at ON token_logs(created_at DESC);

-- ── telegram_dispatches ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS telegram_dispatches (
    id              BIGSERIAL PRIMARY KEY,
    article_id      BIGINT NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    chat_id         TEXT NOT NULL,
    message_id      BIGINT,                 -- Telegram message_id on success
    payload         TEXT,                   -- Full JSON payload sent
    status          VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending|success|failed
    attempt_count   SMALLINT NOT NULL DEFAULT 0,
    last_error      TEXT,
    sent_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tg_dispatches_article_id ON telegram_dispatches(article_id);
CREATE INDEX IF NOT EXISTS idx_tg_dispatches_status     ON telegram_dispatches(status);

-- ── run_logs (Orchestrator audit) ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS run_logs (
    id              BIGSERIAL PRIMARY KEY,
    run_id          UUID NOT NULL DEFAULT uuid_generate_v4(),
    phase           VARCHAR(50) NOT NULL,   -- 'scout'|'analyze'|'dispatch'
    status          VARCHAR(20) NOT NULL,   -- 'started'|'success'|'error'
    articles_found  INTEGER DEFAULT 0,
    articles_saved  INTEGER DEFAULT 0,
    error_message   TEXT,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at     TIMESTAMPTZ
);
