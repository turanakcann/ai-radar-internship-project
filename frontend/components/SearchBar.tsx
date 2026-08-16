"use client";

import { useState, useRef, type FormEvent } from "react";

interface SearchBarProps {
  onSearch: (query: string) => void;
  loading?: boolean;
  placeholder?: string;
}

const HINTS = [
  "edge AI deployment",
  "YOLO object detection",
  "RAG pipeline optimization",
  "LLM fine-tuning techniques",
];

export function SearchBar({ onSearch, loading, placeholder = "Describe what you're looking for…" }: SearchBarProps) {
  const [value, setValue] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const q = value.trim();
    if (q.length >= 3) onSearch(q);
  };

  const canSearch = value.trim().length >= 3;

  return (
    <div style={{ width: "100%" }}>
      {/* Double-bezel search container */}
      <div className="card-shell" style={{ borderRadius: "20px" }}>
        <div
          className="card-core"
          style={{ borderRadius: "15px", padding: "0" }}
        >
          <form
            onSubmit={handleSubmit}
            style={{ display: "flex", alignItems: "center", gap: "12px", padding: "14px 16px" }}
          >
            {/* Search icon */}
            <span
              style={{
                fontSize: "16px",
                flexShrink: 0,
                color: loading ? "#7c3aed" : "rgba(100,116,139,0.7)",
                animation: loading ? "score-pulse 1s ease-in-out infinite" : "none",
                display: "flex",
                alignItems: "center",
              }}
            >
              {loading ? "◌" : "◎"}
            </span>

            {/* Input */}
            <input
              ref={inputRef}
              type="text"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder={placeholder}
              minLength={3}
              disabled={loading}
              aria-label="Semantic search query"
              style={{
                flex: 1,
                background: "transparent",
                border: "none",
                outline: "none",
                fontSize: "14px",
                color: "#e8e8f2",
                fontFamily: "var(--font-sans)",
                letterSpacing: "-0.01em",
              }}
            />

            {/* Submit — button-in-button pattern */}
            {canSearch && !loading && (
              <button
                type="submit"
                className="btn-island btn-primary"
                style={{ fontSize: "12px", padding: "6px 14px 6px 16px", flexShrink: 0 }}
              >
                Search
                <span
                  className="btn-island-icon"
                  style={{
                    width: "22px",
                    height: "22px",
                    background: "rgba(0,212,255,0.12)",
                    fontSize: "10px",
                    color: "#00d4ff",
                  }}
                >
                  ↗
                </span>
              </button>
            )}
          </form>
        </div>
      </div>

      {/* Suggestion chips */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "12px" }}>
        <span style={{ fontSize: "10px", color: "#334155", alignSelf: "center", fontWeight: 500 }}>Try:</span>
        {HINTS.map((hint) => (
          <button
            key={hint}
            type="button"
            onClick={() => { setValue(hint); onSearch(hint); }}
            style={{
              fontSize: "11px",
              padding: "4px 12px",
              borderRadius: "999px",
              border: "1px solid rgba(255,255,255,0.07)",
              background: "rgba(255,255,255,0.03)",
              color: "rgba(100,116,139,0.7)",
              cursor: "pointer",
              fontFamily: "var(--font-sans)",
              transition: "all 300ms cubic-bezier(0.32,0.72,0,1)",
            }}
            onMouseEnter={e => {
              const el = e.currentTarget as HTMLElement;
              el.style.color = "#c4b5fd";
              el.style.borderColor = "rgba(124,58,237,0.3)";
              el.style.background = "rgba(124,58,237,0.08)";
            }}
            onMouseLeave={e => {
              const el = e.currentTarget as HTMLElement;
              el.style.color = "rgba(100,116,139,0.7)";
              el.style.borderColor = "rgba(255,255,255,0.07)";
              el.style.background = "rgba(255,255,255,0.03)";
            }}
          >
            {hint}
          </button>
        ))}
      </div>
    </div>
  );
}
