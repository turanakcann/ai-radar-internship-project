-- fix_schema.sql
-- Fix missing token_logs.total_tokens column and patch mock article metadata.

ALTER TABLE token_logs
ADD COLUMN IF NOT EXISTS total_tokens INTEGER DEFAULT 0;

-- Update mock article URL and associate it with the ArXiv source.
UPDATE articles
SET url = 'https://arxiv.org/abs/2304.08485'
WHERE url = 'https://arxiv.org/abs/2608.demo_yolo';

UPDATE articles
SET source_id = (
    SELECT id FROM sources WHERE lower(name) = 'arxiv' LIMIT 1
)
WHERE url = 'https://arxiv.org/abs/2304.08485';
