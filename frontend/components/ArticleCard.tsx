"use client";

import { clsx } from "clsx";
import { ScoreBadge } from "./ScoreBadge";
import type { Article } from "@/lib/api";

const SOURCE_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  arxiv:  { label: "ArXiv",  color: "#60a5fa", bg: "rgba(59,130,246,0.10)" },
  medium: { label: "Medium", color: "#34d399", bg: "rgba(52,211,153,0.10)" },
  github: { label: "GitHub", color: "#a78bfa", bg: "rgba(167,139,250,0.10)" },
};

const CATEGORY_COLOR: Record<string, string> = {
  "Computer Vision":            "#38bdf8",
  "Large Language Models":      "#c4b5fd",
  "Edge AI":                    "#fb923c",
  "Natural Language Processing": "#2dd4bf",
  "Generative AI":              "#f472b6",
  "Multimodal AI":              "#fbbf24",
  "MLOps":                      "#94a3b8",
  "Robotics":                   "#f87171",
};

interface ArticleCardProps {
  article: Article;
  similarityScore?: number;
  animationDelay?: number;
}

export function ArticleCard({ article, similarityScore, animationDelay = 0 }: ArticleCardProps) {
  const srcKey = article.source_name?.toLowerCase() ?? "unknown";
  const src = SOURCE_CONFIG[srcKey];
  const catColor = CATEGORY_COLOR[article.primary_category ?? ""] ?? "#64748b";
  const isHigh = article.relevance_score !== null && article.relevance_score >= 7.5;

  const publishedDate = article.published_at
    ? new Date(article.published_at).toLocaleDateString("en-GB", {
        day: "2-digit", month: "short", year: "numeric",
      })
    : null;

  return (
    /* ── Outer shell (bezel tray) — h-full lets the grid stretch it ── */
    <div
      className={clsx("card-shell animate-fade-in", isHigh && "score-hi")}
      style={{ animationDelay: `${animationDelay}ms`, height: "100%", display: "flex", flexDirection: "column" }}
    >
      {/* ── Inner core (glass plate) — flex col so footer sticks to bottom ── */}
      <div className="card-core" style={{ padding: "20px", flex: 1, display: "flex", flexDirection: "column", gap: "16px" }}>

        {/* ── Header row ── */}
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: "12px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>

            {/* Source badge */}
            {src ? (
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  padding: "3px 10px",
                  borderRadius: "999px",
                  fontSize: "10px",
                  fontWeight: 700,
                  letterSpacing: "0.1em",
                  textTransform: "uppercase",
                  color: src.color,
                  background: src.bg,
                  border: `1px solid ${src.color}30`,
                }}
              >
                {src.label}
              </span>
            ) : (
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  padding: "3px 10px",
                  borderRadius: "999px",
                  fontSize: "10px",
                  fontWeight: 600,
                  letterSpacing: "0.08em",
                  textTransform: "uppercase",
                  color: "rgba(148,163,184,0.7)",
                  background: "rgba(255,255,255,0.04)",
                  border: "1px solid rgba(255,255,255,0.08)",
                }}
              >
                {article.source_name ?? "Unknown"}
              </span>
            )}

            {/* Category */}
            {article.primary_category && (
              <span style={{ fontSize: "11px", fontWeight: 500, color: catColor }}>
                {article.primary_category}
              </span>
            )}

            {/* Dispatched indicator */}
            {article.is_dispatched && (
              <span
                title="Dispatched to Telegram"
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  padding: "2px 8px",
                  borderRadius: "999px",
                  fontSize: "9px",
                  fontWeight: 600,
                  letterSpacing: "0.08em",
                  textTransform: "uppercase",
                  color: "#c4b5fd",
                  background: "rgba(124,58,237,0.10)",
                  border: "1px solid rgba(124,58,237,0.25)",
                  gap: "4px",
                }}
              >
                ✦ Sent
              </span>
            )}
          </div>

          <ScoreBadge score={article.relevance_score} />
        </div>

        {/* ── Title ── */}
        <h2
          style={{
            fontSize: "15px",
            fontWeight: 600,
            lineHeight: "1.45",
            letterSpacing: "-0.01em",
            color: "#e8e8f2",
            display: "-webkit-box",
            WebkitLineClamp: 2,
            WebkitBoxOrient: "vertical",
            overflow: "hidden",
          }}
        >
          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              color: "inherit",
              textDecoration: "none",
              transition: "color 400ms cubic-bezier(0.32,0.72,0,1)",
            }}
            onMouseEnter={e => ((e.currentTarget as HTMLElement).style.color = "#38bdf8")}
            onMouseLeave={e => ((e.currentTarget as HTMLElement).style.color = "#e8e8f2")}
          >
            {article.title}
          </a>
        </h2>

        {/* ── Expandable middle: bullets + tags — pushes footer down ── */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "12px" }}>
          {/* ── Summary bullets ── */}
          {article.summary_bullets.length > 0 && (
            <ul style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              {article.summary_bullets.map((bullet, i) => (
                <li
                  key={i}
                  style={{
                    display: "flex",
                    gap: "8px",
                    fontSize: "12.5px",
                    lineHeight: "1.55",
                    color: "rgba(148,163,184,0.85)",
                  }}
                >
                  <span style={{ color: "#7c3aed", flexShrink: 0, marginTop: "1px", fontSize: "10px" }}>▸</span>
                  <span>{bullet}</span>
                </li>
              ))}
            </ul>
          )}

          {/* ── Tags ── */}
          {article.tags.length > 0 && (
            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
              {article.tags.slice(0, 6).map((tag) => (
                <span
                  key={tag}
                  style={{
                    fontSize: "10px",
                    padding: "3px 8px",
                    borderRadius: "6px",
                    background: "rgba(255,255,255,0.04)",
                    color: "rgba(148,163,184,0.7)",
                    border: "1px solid rgba(255,255,255,0.07)",
                    transition: "all 300ms cubic-bezier(0.32,0.72,0,1)",
                    cursor: "default",
                    fontWeight: 500,
                    letterSpacing: "0.02em",
                  }}
                  onMouseEnter={e => {
                    const el = e.currentTarget as HTMLElement;
                    el.style.color = "#c4b5fd";
                    el.style.borderColor = "rgba(124,58,237,0.3)";
                    el.style.background = "rgba(124,58,237,0.08)";
                  }}
                  onMouseLeave={e => {
                    const el = e.currentTarget as HTMLElement;
                    el.style.color = "rgba(148,163,184,0.7)";
                    el.style.borderColor = "rgba(255,255,255,0.07)";
                    el.style.background = "rgba(255,255,255,0.04)";
                  }}
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* ── Footer ── */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            paddingTop: "12px",
            borderTop: "1px solid rgba(255,255,255,0.05)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "14px", fontSize: "11px", color: "#475569" }}>
            {article.author && (
              <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                <span style={{ opacity: 0.6 }}>◎</span>
                <span style={{ maxWidth: "120px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {article.author}
                </span>
              </span>
            )}
            {publishedDate && (
              <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                <span style={{ opacity: 0.6 }}>◷</span>
                {publishedDate}
              </span>
            )}
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            {similarityScore !== undefined && (
              <span style={{ fontSize: "10px", color: "#00d4ff", fontFamily: "var(--font-mono)", fontWeight: 600 }}>
                {(similarityScore * 100).toFixed(0)}% match
              </span>
            )}
            <a
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-island"
              style={{
                fontSize: "11px",
                padding: "5px 12px 5px 14px",
                color: "rgba(148,163,184,0.8)",
                background: "rgba(255,255,255,0.04)",
                border: "1px solid rgba(255,255,255,0.08)",
                textDecoration: "none",
              }}
              onMouseEnter={e => {
                const el = e.currentTarget as HTMLElement;
                el.style.color = "#38bdf8";
                el.style.borderColor = "rgba(0,212,255,0.3)";
                el.style.background = "rgba(0,212,255,0.06)";
              }}
              onMouseLeave={e => {
                const el = e.currentTarget as HTMLElement;
                el.style.color = "rgba(148,163,184,0.8)";
                el.style.borderColor = "rgba(255,255,255,0.08)";
                el.style.background = "rgba(255,255,255,0.04)";
              }}
            >
              Read ↗
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
