-- init_sources.sql
-- Creates the sources table and inserts mock seed data for the Tech Radar backend.

CREATE TABLE IF NOT EXISTS sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    base_url TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

INSERT INTO sources (name, base_url, is_active)
VALUES
    ('arxiv', 'https://arxiv.org', TRUE),
    ('medium', 'https://medium.com', TRUE),
    ('github', 'https://github.com', TRUE)
ON CONFLICT (name) DO NOTHING;
