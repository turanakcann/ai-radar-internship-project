"use client";

import { useState } from "react";
import { searchArticles, type SearchResult } from "@/lib/api";
import { SearchBar } from "@/components/SearchBar";
import { ArticleCard } from "@/components/ArticleCard";

export default function SearchPage() {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastQuery, setLastQuery] = useState("");

  const handleSearch = async (query: string) => {
    setLoading(true);
    setError(null);
    setLastQuery(query);

    try {
      const data = await searchArticles(query, 20);
      setResults(data);
      setSearched(true);
    } catch (e: any) {
      setError(e.message ?? "Search failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "1000px", margin: "0 auto", padding: "48px 24px" }}>

      {/* ── Hero ── */}
      <div className="animate-fade-in" style={{ marginBottom: "40px" }}>
        <div className="eyebrow" style={{ marginBottom: "16px" }}>
          <span style={{ fontSize: "8px" }}>◎</span>
          Semantic Search
        </div>
        <h1
          style={{
            fontSize: "clamp(28px, 4.5vw, 46px)",
            fontWeight: 800,
            letterSpacing: "-0.03em",
            lineHeight: 1.15,
            marginBottom: "12px",
          }}
        >
          Vector{" "}
          <span className="gradient-text-cyan">Intelligence Search</span>
        </h1>
        <p style={{ fontSize: "14px", color: "rgba(100,116,139,0.9)", lineHeight: 1.6 }}>
          Search indexed articles by meaning, not keywords — powered by OpenAI embeddings and ChromaDB.
        </p>
      </div>

      {/* ── Search Bar ── */}
      <div className="animate-fade-in" style={{ marginBottom: "40px", animationDelay: "80ms" }}>
        <SearchBar onSearch={handleSearch} loading={loading} />
      </div>

      {/* ── Error ── */}
      {error && (
        <div className="card-shell animate-fade-in" style={{ borderRadius: "18px", marginBottom: "24px" }}>
          <div
            className="card-core"
            style={{
              borderRadius: "13px",
              padding: "20px 24px",
              borderColor: "rgba(248,113,113,0.2)",
              display: "flex",
              alignItems: "center",
              gap: "12px",
            }}
          >
            <span style={{ color: "#f87171", fontSize: "16px", flexShrink: 0 }}>⊗</span>
            <p style={{ fontSize: "13px", color: "#fca5a5" }}>{error}</p>
          </div>
        </div>
      )}

      {/* ── Results ── */}
      {searched && !loading && !error && (
        <div>
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
            {results.length > 0 ? (
              <>
                <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "#10ffa0", display: "inline-block" }} />
                Found <strong style={{ color: "#e8e8f2" }}>{results.length}</strong> results for{" "}
                <em style={{ color: "#7c3aed", fontStyle: "normal", fontWeight: 600 }}>"{lastQuery}"</em>
              </>
            ) : (
              <>
                <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "#f87171", display: "inline-block" }} />
                No semantic matches found for <em style={{ color: "#64748b", fontStyle: "normal" }}>"{lastQuery}"</em>
              </>
            )}
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "16px" }}>
            {results.map((result, idx) => (
              <ArticleCard
                key={result.article.id}
                article={result.article}
                similarityScore={result.similarity_score}
                animationDelay={idx * 50}
              />
            ))}
          </div>
        </div>
      )}

      {/* ── Empty state (before search) ── */}
      {!searched && !loading && (
        <div
          className="animate-fade-in"
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            padding: "80px 32px",
            textAlign: "center",
            animationDelay: "120ms",
          }}
        >
          <div
            className="card-shell"
            style={{
              display: "inline-flex",
              padding: "6px",
              borderRadius: "24px",
              marginBottom: "24px",
            }}
          >
            <div
              className="card-core"
              style={{
                width: "72px",
                height: "72px",
                borderRadius: "19px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "30px",
                color: "rgba(124,58,237,0.4)",
              }}
            >
              ◎
            </div>
          </div>
          <p style={{ fontSize: "15px", color: "rgba(100,116,139,0.8)", marginBottom: "8px" }}>
            Ask a question, describe a concept, or paste a research topic.
          </p>
          <p style={{ fontSize: "12px", color: "rgba(71,85,105,0.6)" }}>
            The engine finds articles that match the <em>meaning</em> of your query.
          </p>
        </div>
      )}
    </div>
  );
}
