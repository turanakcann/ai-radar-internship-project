-- ═══════════════════════════════════════════════════════════════════════════
-- Migration 001: Fix summary_bullets type + Create telegram_dispatches table
-- Run this in Supabase Dashboard → SQL Editor
-- ═══════════════════════════════════════════════════════════════════════════

-- ── 1. Fix summary_bullets column type (JSONB → TEXT[]) ─────────────────────
-- The SQLAlchemy model uses ARRAY(Text), but the column was created as JSONB.
-- This ALTER safely converts any existing JSONB string arrays to TEXT[].

ALTER TABLE articles
  ALTER COLUMN summary_bullets TYPE TEXT[]
  USING CASE
    WHEN summary_bullets IS NULL THEN NULL
    WHEN jsonb_typeof(summary_bullets) = 'array' THEN
      ARRAY(SELECT jsonb_array_elements_text(summary_bullets))
    ELSE
      ARRAY[summary_bullets::text]
  END;

-- ── 2. Fix tags column type if also JSONB (same mismatch may exist) ──────────
ALTER TABLE articles
  ALTER COLUMN tags TYPE TEXT[]
  USING CASE
    WHEN tags IS NULL THEN NULL
    WHEN jsonb_typeof(tags) = 'array' THEN
      ARRAY(SELECT jsonb_array_elements_text(tags))
    ELSE
      ARRAY[tags::text]
  END;

-- ── 3. Create telegram_dispatches table ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS telegram_dispatches (
    id            BIGSERIAL PRIMARY KEY,
    article_id    BIGINT NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    chat_id       VARCHAR(100) NOT NULL,
    message_id    BIGINT,
    payload       VARCHAR(4096),
    status        VARCHAR(20) NOT NULL DEFAULT 'pending',
    attempt_count SMALLINT NOT NULL DEFAULT 0,
    last_error    VARCHAR(2048),
    sent_at       TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for fast lookup of pending dispatches per article
CREATE INDEX IF NOT EXISTS idx_telegram_dispatches_article_id
    ON telegram_dispatches(article_id);

CREATE INDEX IF NOT EXISTS idx_telegram_dispatches_status
    ON telegram_dispatches(status, created_at DESC);
