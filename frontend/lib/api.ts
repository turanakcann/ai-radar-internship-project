/**
 * lib/api.ts — Typed API client for the FastAPI backend.
 */

export const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? '/api';

export interface Article {
  id: number;
  source_name: string;
  url: string;
  title: string;
  author: string | null;
  published_at: string | null;
  relevance_score: number | null;
  primary_category: string | null;
  tags: string[];
  summary_bullets: string[];
  is_dispatched: boolean;
  created_at: string;
}

export interface SearchResult {
  article: Article;
  similarity_score: number;
}

export interface PipelineStats {
  total_articles: number;
  articles_by_source: Record<string, number>;
  articles_by_category: Record<string, number>;
  total_tokens_spent: number;
  total_cost_usd: number;
  dispatched_count: number;
  daily_ingestion: Array<{ date: string; count: number; avg_score: number }>;
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? 'API Error');
  }
  return res.json() as Promise<T>;
}

// ── Articles ──────────────────────────────────────────────────────────────────

export interface ArticlesParams {
  page?: number;
  page_size?: number;
  source?: string;
  category?: string;
  min_score?: number;
  dispatched?: boolean;
  date_from?: string;  // ISO datetime string
  date_to?: string;    // ISO datetime string
}

export async function fetchArticles(params: ArticlesParams = {}): Promise<Article[]> {
  const query = new URLSearchParams();
  if (params.page) query.set('page', String(params.page));
  if (params.page_size) query.set('page_size', String(params.page_size));
  if (params.source) query.set('source', params.source);
  if (params.category) query.set('category', params.category);
  if (params.min_score !== undefined) query.set('min_score', String(params.min_score));
  if (params.dispatched !== undefined) query.set('dispatched', String(params.dispatched));
  if (params.date_from) query.set('date_from', params.date_from);
  if (params.date_to) query.set('date_to', params.date_to);

  return apiFetch<Article[]>(`/articles?${query.toString()}`);
}

export async function fetchArticle(id: number): Promise<Article> {
  return apiFetch<Article>(`/articles/${id}`);
}

// ── Search ────────────────────────────────────────────────────────────────────

export async function searchArticles(
  query: string,
  top_k = 10,
  min_score = 0,
): Promise<SearchResult[]> {
  return apiFetch<SearchResult[]>('/search', {
    method: 'POST',
    body: JSON.stringify({ query, top_k, min_score }),
  });
}

// ── Stats ─────────────────────────────────────────────────────────────────────

export async function fetchStats(): Promise<PipelineStats> {
  return apiFetch<PipelineStats>('/stats');
}

// ── Pipeline Trigger ──────────────────────────────────────────────────────────

export async function triggerPipeline(): Promise<{ run_id: string; status: string; message: string }> {
  return apiFetch('/run', { method: 'POST' });
}

export async function getPipelineStatus(): Promise<{ running: boolean }> {
  return apiFetch('/run/status');
}
