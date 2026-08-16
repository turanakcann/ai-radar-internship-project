"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { fetchArticles, type Article } from "@/lib/api";
import { ArticleCard } from "@/components/ArticleCard";
import { CategoryFilter, type SourceFilter, type CategoryFilter as CatFilter } from "@/components/CategoryFilter";

const PAGE_SIZE = 12;

/* ── Loading skeleton cards ─────────────────────────────── */
function SkeletonCard() {
  return (
    <div className="card-shell" style={{ borderRadius: "28px" }}>
      <div className="card-core" style={{ padding: "20px", borderRadius: "23px" }}>
        <div style={{ display: "flex", gap: "8px", marginBottom: "16px" }}>
          <div className="shimmer" style={{ height: "20px", width: "60px", borderRadius: "999px" }} />
          <div className="shimmer" style={{ height: "20px", width: "80px", borderRadius: "999px" }} />
        </div>
        <div className="shimmer" style={{ height: "18px", width: "90%", borderRadius: "6px", marginBottom: "8px" }} />
        <div className="shimmer" style={{ height: "18px", width: "70%", borderRadius: "6px", marginBottom: "20px" }} />
        <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
          <div className="shimmer" style={{ height: "12px", width: "100%", borderRadius: "4px" }} />
          <div className="shimmer" style={{ height: "12px", width: "88%", borderRadius: "4px" }} />
          <div className="shimmer" style={{ height: "12px", width: "94%", borderRadius: "4px" }} />
        </div>
      </div>
    </div>
  );
}

export default function FeedPage() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [isOffline, setIsOffline] = useState(false);

  // Filters
  const [source, setSource] = useState<SourceFilter>("all");
  const [category, setCategory] = useState<CatFilter>("all");
  const [minScore, setMinScore] = useState(0);

  // Ref-based page counter — updates synchronously so no stale-closure race.
  // Using a ref (not state) means mutations are instant and never out-of-sync
  // with the fetch that reads them.
  const nextPageRef = useRef(1);

  // Strict Mode double-mount guard: ensures the initial fetch runs only once
  // even though React 18 mounts → unmounts → remounts in development.
  const initialisedRef = useRef(false);

  const loadArticles = useCallback(
    async (resetPage = false) => {
      if (resetPage) {
        setLoading(true);
        setArticles([]);
        nextPageRef.current = 1;
      } else {
        setLoadingMore(true);
      }
      setError(null);

      const pageToFetch = nextPageRef.current;

      try {
        const params = {
          page: pageToFetch,
          page_size: PAGE_SIZE,
          ...(source !== "all" && { source }),
          ...(category !== "all" && { category }),
          ...(minScore > 0 && { min_score: minScore }),
        };
        const data = await fetchArticles(params);
        setError(null);
        setIsOffline(false);

        // Always dedup by id — protects against any server-side pagination
        // overlap and React 18 Strict Mode double-invocation edge cases.
        setArticles((prev) => {
          const existingIds = new Set(prev.map((a) => a.id));
          const fresh = data.filter((a) => !existingIds.has(a.id));
          // Only advance the page counter when we actually have new articles,
          // so a duplicate-free empty diff doesn't silently skip a page.
          if (fresh.length > 0 || resetPage) {
            nextPageRef.current = pageToFetch + 1;
          }
          return resetPage ? data : [...prev, ...fresh];
        });
        setHasMore(data.length === PAGE_SIZE);
      } catch (e: any) {
        const isServiceError =
          typeof e?.message === "string" &&
          (e.message.includes("503") || e.message.includes("Service unavailable"));
        const message = isServiceError
          ? "Backend is offline — check that your FastAPI server is running."
          : (e?.message ?? "Failed to load articles.");
        setError(message);
        setIsOffline(isServiceError);
      } finally {
        setLoading(false);
        setLoadingMore(false);
      }
    },
    [source, category, minScore]
  );

  // Reset and reload whenever filters change.
  // The `initialisedRef` guard prevents Strict Mode's double-mount from
  // firing two concurrent fetches that each return page 1, which would
  // produce duplicate article IDs and the "key='1'" React warning.
  useEffect(() => {
    if (!initialisedRef.current) {
      initialisedRef.current = true;
    }
    loadArticles(true);
  }, [source, category, minScore]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div style={{ maxWidth: "1280px", margin: "0 auto", padding: "48px 24px" }}>

      {/* ── Hero ─────────────────────────────────────────── */}
      <div className="animate-fade-in" style={{ marginBottom: "48px" }}>
        <div className="eyebrow" style={{ marginBottom: "16px" }}>
          <span style={{ fontSize: "8px" }}>◈</span>
          Intelligence Feed
        </div>
        <h1
          style={{
            fontSize: "clamp(32px, 5vw, 52px)",
            fontWeight: 800,
            letterSpacing: "-0.03em",
            lineHeight: 1.1,
            marginBottom: "16px",
          }}
        >
          AI & ML{" "}
          <span className="gradient-text-primary">Tech Radar</span>
        </h1>
        <p style={{ fontSize: "15px", color: "rgba(100,116,139,0.9)", maxWidth: "500px", lineHeight: 1.6 }}>
          Autonomous intelligence from ArXiv, Medium, and GitHub —
          scored and summarized by multi-agent AI.
        </p>
      </div>

      {/* ── Two-column layout ─────────────────────────────── */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "240px 1fr",
          gap: "24px",
          alignItems: "start",
        }}
        className="feed-grid"
      >
        {/* Sidebar — sticky */}
        <div style={{ position: "sticky", top: "88px", animationDelay: "80ms" }} className="animate-fade-in">
          <CategoryFilter
            source={source}
            category={category}
            minScore={minScore}
            onSourceChange={(v) => setSource(v)}
            onCategoryChange={(v) => setCategory(v)}
            onMinScoreChange={(v) => setMinScore(v)}
          />
        </div>

        {/* ── Feed column ── */}
        <div>
          {loading ? (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: "16px" }}>
              {Array.from({ length: 6 }).map((_, i) => (
                <SkeletonCard key={i} />
              ))}
            </div>
          ) : isOffline ? (
            /* 503 / Offline state */
            <div className="card-shell animate-fade-in" style={{ borderRadius: "28px" }}>
              <div
                className="card-core"
                style={{
                  borderRadius: "23px",
                  padding: "48px 32px",
                  textAlign: "center",
                  borderColor: "rgba(0,212,255,0.15)",
                  boxShadow: "0 0 40px rgba(0,212,255,0.06), inset 0 1px 1px rgba(255,255,255,0.08)",
                }}
              >
                <div
                  style={{
                    width: "52px",
                    height: "52px",
                    borderRadius: "50%",
                    background: "rgba(0,212,255,0.08)",
                    border: "1px solid rgba(0,212,255,0.2)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    margin: "0 auto 20px",
                    fontSize: "22px",
                  }}
                >
                  ⊡
                </div>
                <p style={{ fontSize: "11px", fontWeight: 700, letterSpacing: "0.15em", textTransform: "uppercase", color: "#38bdf8", marginBottom: "12px" }}>
                  Backend Offline
                </p>
                <p style={{ fontSize: "15px", color: "rgba(148,163,184,0.8)", maxWidth: "380px", margin: "0 auto 24px", lineHeight: 1.6 }}>
                  The API server is not responding. Start your FastAPI backend and try again.
                </p>
                <button
                  onClick={() => loadArticles(true)}
                  className="btn-island btn-primary"
                >
                  Retry connection
                  <span className="btn-island-icon" style={{ background: "rgba(0,212,255,0.12)", color: "#00d4ff", width: "28px", height: "28px", fontSize: "12px" }}>
                    ↻
                  </span>
                </button>
              </div>
            </div>
          ) : error ? (
            /* Generic error */
            <div className="card-shell animate-fade-in" style={{ borderRadius: "22px" }}>
              <div className="card-core" style={{ borderRadius: "17px", padding: "32px 24px", textAlign: "center" }}>
                <p style={{ fontSize: "13px", color: "#f87171", marginBottom: "16px" }}>{error}</p>
                <button
                  onClick={() => loadArticles(true)}
                  className="btn-island"
                  style={{
                    fontSize: "12px",
                    padding: "6px 16px",
                    background: "rgba(248,113,113,0.08)",
                    border: "1px solid rgba(248,113,113,0.25)",
                    color: "#fca5a5",
                  }}
                >
                  ↻ Retry
                </button>
              </div>
            </div>
          ) : articles.length === 0 ? (
            /* Empty state */
            <div className="card-shell animate-fade-in" style={{ borderRadius: "28px" }}>
              <div
                className="card-core"
                style={{
                  borderRadius: "23px",
                  padding: "64px 32px",
                  textAlign: "center",
                }}
              >
                <div style={{ fontSize: "40px", marginBottom: "20px", opacity: 0.3 }}>◎</div>
                <p style={{ fontSize: "15px", color: "rgba(100,116,139,0.8)", marginBottom: "8px" }}>
                  No articles match these filters.
                </p>
                <p style={{ fontSize: "12px", color: "rgba(71,85,105,0.7)" }}>
                  Run the pipeline to ingest new articles, or loosen your filters.
                </p>
              </div>
            </div>
          ) : (
            <>
              {/* Article count */}
              <div
                className="animate-fade-in"
                style={{
                  fontSize: "11px",
                  color: "#475569",
                  marginBottom: "20px",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                }}
              >
                <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "#10ffa0", display: "inline-block" }} />
                <span>
                  Showing <strong style={{ color: "#e8e8f2" }}>{articles.length}</strong> articles
                </span>
              </div>

              {/* Equal-height CSS grid — auto-rows-fr stretches every card
                   to the tallest in its row, preventing ragged bottoms.    */}
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(2, 1fr)",
                  gridAutoRows: "1fr",
                  gap: "16px",
                }}
                className="article-grid"
              >
                {articles.map((article, idx) => (
                  <ArticleCard
                    key={`article-${article.id}`}
                    article={article}
                    animationDelay={Math.min(idx * 45, 500)}
                  />
                ))}
              </div>

              {/* Load more */}
              {hasMore && (
                <div style={{ marginTop: "32px", textAlign: "center" }}>
                  <button
                    onClick={() => loadArticles(false)}
                    disabled={loadingMore}
                    className="btn-island"
                    style={{
                      fontSize: "13px",
                      padding: "10px 24px 10px 28px",
                      background: "rgba(124,58,237,0.08)",
                      border: "1px solid rgba(124,58,237,0.25)",
                      color: "#c4b5fd",
                      opacity: loadingMore ? 0.5 : 1,
                    }}
                  >
                    {loadingMore ? (
                      <>
                        <span style={{ animation: "score-pulse 1s ease-in-out infinite" }}>◌</span>
                        Loading…
                      </>
                    ) : (
                      <>
                        Load more articles
                        <span
                          className="btn-island-icon"
                          style={{
                            width: "26px",
                            height: "26px",
                            background: "rgba(124,58,237,0.15)",
                            color: "#7c3aed",
                            fontSize: "10px",
                          }}
                        >
                          ↓
                        </span>
                      </>
                    )}
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Responsive overrides */}
      <style>{`
        @media (max-width: 768px) {
          .feed-grid {
            grid-template-columns: 1fr !important;
          }
          .article-grid {
            grid-template-columns: 1fr !important;
          }
        }
        @media (min-width: 1200px) {
          .article-grid {
            grid-template-columns: repeat(3, 1fr) !important;
          }
        }
      `}</style>
    </div>
  );
}
