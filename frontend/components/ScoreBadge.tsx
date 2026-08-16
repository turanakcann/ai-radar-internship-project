"use client";

interface ScoreBadgeProps {
  score: number | null;
  size?: "sm" | "md" | "lg";
}

function getScoreConfig(score: number): { emoji: string; label: string; color: string; bg: string; border: string } {
  if (score >= 9.0) return { emoji: "🔥", label: "Critical",  color: "#fca5a5", bg: "rgba(239,68,68,0.12)",  border: "rgba(239,68,68,0.35)" };
  if (score >= 8.0) return { emoji: "🔥", label: "High",      color: "#fb923c", bg: "rgba(249,115,22,0.12)", border: "rgba(249,115,22,0.35)" };
  if (score >= 7.5) return { emoji: "⚡", label: "Notable",   color: "#fbbf24", bg: "rgba(245,158,11,0.12)", border: "rgba(245,158,11,0.35)" };
  if (score >= 6.0) return { emoji: "◈", label: "Relevant",  color: "#38bdf8", bg: "rgba(0,212,255,0.10)",  border: "rgba(0,212,255,0.30)" };
  if (score >= 4.0) return { emoji: "○", label: "Moderate",  color: "#64748b", bg: "rgba(100,116,139,0.10)", border: "rgba(100,116,139,0.25)" };
  return                    { emoji: "○", label: "Low",       color: "#475569", bg: "rgba(71,85,105,0.08)",  border: "rgba(71,85,105,0.20)" };
}

const SIZE_STYLES = {
  sm: { fontSize: "10px", padding: "2px 7px" },
  md: { fontSize: "11px", padding: "3px 9px" },
  lg: { fontSize: "12px", padding: "4px 11px" },
};

export function ScoreBadge({ score, size = "md" }: ScoreBadgeProps) {
  if (score === null || score === undefined) {
    return (
      <span
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "5px",
          ...SIZE_STYLES[size],
          borderRadius: "999px",
          border: "1px solid rgba(71,85,105,0.25)",
          background: "rgba(71,85,105,0.08)",
          color: "#475569",
          fontWeight: 600,
          fontFamily: "var(--font-mono)",
        }}
      >
        —
      </span>
    );
  }

  const { emoji, label, color, bg, border } = getScoreConfig(score);
  const isHigh = score >= 7.5;

  return (
    <span
      className={isHigh ? "score-pulse" : undefined}
      title={`Relevance: ${score.toFixed(1)}/10 — ${label}`}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "5px",
        ...SIZE_STYLES[size],
        borderRadius: "999px",
        border: `1px solid ${border}`,
        background: bg,
        color,
        fontWeight: 700,
        fontFamily: "var(--font-mono)",
        letterSpacing: "0.01em",
        flexShrink: 0,
      }}
    >
      <span style={{ fontSize: "0.9em" }}>{emoji}</span>
      <span>{score.toFixed(1)}</span>
    </span>
  );
}
