"use client";

import { clsx } from "clsx";

export type SourceFilter = "all" | "arxiv" | "medium" | "github";
export type CategoryFilter =
  | "all"
  | "Computer Vision"
  | "Large Language Models"
  | "Edge AI"
  | "Natural Language Processing"
  | "Generative AI"
  | "Multimodal AI"
  | "MLOps"
  | "Robotics";

interface CategoryFilterProps {
  source: SourceFilter;
  category: CategoryFilter;
  minScore: number;
  onSourceChange: (v: SourceFilter) => void;
  onCategoryChange: (v: CategoryFilter) => void;
  onMinScoreChange: (v: number) => void;
}

const SOURCES: { value: SourceFilter; label: string; color: string; activeBg: string }[] = [
  { value: "all",    label: "All",    color: "#94a3b8", activeBg: "rgba(148,163,184,0.12)" },
  { value: "arxiv",  label: "ArXiv",  color: "#60a5fa", activeBg: "rgba(59,130,246,0.12)"  },
  { value: "medium", label: "Medium", color: "#34d399", activeBg: "rgba(52,211,153,0.12)"  },
  { value: "github", label: "GitHub", color: "#a78bfa", activeBg: "rgba(167,139,250,0.12)" },
];

const CATEGORIES: { value: CategoryFilter; label: string }[] = [
  { value: "all",                         label: "All categories" },
  { value: "Computer Vision",             label: "Computer Vision" },
  { value: "Large Language Models",       label: "LLMs" },
  { value: "Edge AI",                     label: "Edge AI" },
  { value: "Natural Language Processing", label: "NLP" },
  { value: "Generative AI",               label: "Generative AI" },
  { value: "Multimodal AI",               label: "Multimodal" },
  { value: "MLOps",                       label: "MLOps" },
  { value: "Robotics",                    label: "Robotics" },
];

export function CategoryFilter({
  source,
  category,
  minScore,
  onSourceChange,
  onCategoryChange,
  onMinScoreChange,
}: CategoryFilterProps) {
  return (
    /* Outer shell */
    <div className="card-shell" style={{ borderRadius: "20px" }}>
      {/* Inner core */}
      <div className="card-core" style={{ padding: "20px", borderRadius: "15px", display: "flex", flexDirection: "column", gap: "20px" }}>

        {/* Header */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span style={{ color: "#7c3aed", fontSize: "13px" }}>⊟</span>
          <span style={{ fontSize: "11px", fontWeight: 600, letterSpacing: "0.12em", textTransform: "uppercase", color: "rgba(148,163,184,0.7)" }}>
            Filters
          </span>
        </div>

        {/* ── Source ── */}
        <div>
          <div style={{ fontSize: "10px", fontWeight: 600, letterSpacing: "0.08em", textTransform: "uppercase", color: "#475569", marginBottom: "10px" }}>
            Source
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
            {SOURCES.map(({ value, label, color, activeBg }) => {
              const active = source === value;
              return (
                <button
                  key={value}
                  onClick={() => onSourceChange(value)}
                  style={{
                    fontSize: "11px",
                    padding: "5px 12px",
                    borderRadius: "999px",
                    border: `1px solid ${active ? color + "50" : "rgba(255,255,255,0.07)"}`,
                    background: active ? activeBg : "transparent",
                    color: active ? color : "rgba(100,116,139,0.8)",
                    fontWeight: active ? 600 : 400,
                    cursor: "pointer",
                    transition: "all 300ms cubic-bezier(0.32,0.72,0,1)",
                  }}
                  onMouseEnter={e => {
                    if (!active) {
                      const el = e.currentTarget as HTMLElement;
                      el.style.color = color;
                      el.style.borderColor = color + "35";
                      el.style.background = activeBg;
                    }
                  }}
                  onMouseLeave={e => {
                    if (!active) {
                      const el = e.currentTarget as HTMLElement;
                      el.style.color = "rgba(100,116,139,0.8)";
                      el.style.borderColor = "rgba(255,255,255,0.07)";
                      el.style.background = "transparent";
                    }
                  }}
                >
                  {label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Divider */}
        <div style={{ height: "1px", background: "rgba(255,255,255,0.05)" }} />

        {/* ── Category ── */}
        <div>
          <div style={{ fontSize: "10px", fontWeight: 600, letterSpacing: "0.08em", textTransform: "uppercase", color: "#475569", marginBottom: "10px" }}>
            Category
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
            {CATEGORIES.map(({ value, label }) => {
              const active = category === value;
              return (
                <button
                  key={value}
                  onClick={() => onCategoryChange(value)}
                  style={{
                    fontSize: "12px",
                    padding: "7px 12px",
                    borderRadius: "10px",
                    border: "none",
                    background: active ? "rgba(124,58,237,0.15)" : "transparent",
                    color: active ? "#c4b5fd" : "rgba(100,116,139,0.8)",
                    fontWeight: active ? 600 : 400,
                    cursor: "pointer",
                    textAlign: "left",
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    transition: "all 250ms cubic-bezier(0.32,0.72,0,1)",
                  }}
                  onMouseEnter={e => {
                    if (!active) {
                      const el = e.currentTarget as HTMLElement;
                      el.style.color = "#e8e8f2";
                      el.style.background = "rgba(255,255,255,0.04)";
                    }
                  }}
                  onMouseLeave={e => {
                    if (!active) {
                      const el = e.currentTarget as HTMLElement;
                      el.style.color = "rgba(100,116,139,0.8)";
                      el.style.background = "transparent";
                    }
                  }}
                >
                  {active && <span style={{ width: "4px", height: "4px", borderRadius: "50%", background: "#7c3aed", flexShrink: 0 }} />}
                  {label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Divider */}
        <div style={{ height: "1px", background: "rgba(255,255,255,0.05)" }} />

        {/* ── Min Score Slider ── */}
        <div>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
            <span style={{ fontSize: "10px", fontWeight: 600, letterSpacing: "0.08em", textTransform: "uppercase", color: "#475569" }}>
              Min Score
            </span>
            <span style={{ fontSize: "13px", fontWeight: 700, color: "#7c3aed", fontFamily: "var(--font-mono)" }}>
              {minScore.toFixed(1)}
            </span>
          </div>
          <input
            type="range"
            min={0}
            max={10}
            step={0.5}
            value={minScore}
            onChange={(e) => onMinScoreChange(parseFloat(e.target.value))}
            style={{
              width: "100%",
              background: `linear-gradient(to right, #7c3aed ${minScore * 10}%, rgba(255,255,255,0.08) ${minScore * 10}%)`,
            }}
            aria-label="Minimum relevance score filter"
          />
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: "6px", fontSize: "10px", color: "#334155" }}>
            <span>0</span><span>5</span><span>10</span>
          </div>
        </div>

        {/* Reset button */}
        {(source !== "all" || category !== "all" || minScore > 0) && (
          <button
            onClick={() => { onSourceChange("all"); onCategoryChange("all"); onMinScoreChange(0); }}
            style={{
              fontSize: "11px",
              padding: "7px 14px",
              borderRadius: "999px",
              border: "1px solid rgba(255,255,255,0.07)",
              background: "transparent",
              color: "rgba(148,163,184,0.5)",
              cursor: "pointer",
              transition: "all 300ms cubic-bezier(0.32,0.72,0,1)",
              display: "flex",
              alignItems: "center",
              gap: "6px",
              justifyContent: "center",
            }}
            onMouseEnter={e => {
              const el = e.currentTarget as HTMLElement;
              el.style.color = "#e8e8f2";
              el.style.borderColor = "rgba(255,255,255,0.15)";
            }}
            onMouseLeave={e => {
              const el = e.currentTarget as HTMLElement;
              el.style.color = "rgba(148,163,184,0.5)";
              el.style.borderColor = "rgba(255,255,255,0.07)";
            }}
          >
            ✕ Clear filters
          </button>
        )}
      </div>
    </div>
  );
}
