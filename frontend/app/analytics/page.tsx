"use client";

import { useState, useEffect } from "react";
import { fetchStats, type PipelineStats } from "@/lib/api";
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from "recharts";

const CHART_COLORS = {
  violet: "#7c3aed",
  cyan:   "#00d4ff",
  green:  "#10ffa0",
  orange: "#f97316",
  pink:   "#ec4899",
  teal:   "#14b8a6",
  amber:  "#f59e0b",
};

const CATEGORY_COLORS = [
  "#7c3aed", "#00d4ff", "#10ffa0", "#f97316",
  "#ec4899", "#14b8a6", "#f59e0b", "#ef4444",
];

const TOOLTIP_STYLE = {
  backgroundColor: "#0f0f1c",
  border: "1px solid rgba(255,255,255,0.08)",
  borderRadius: "12px",
  fontSize: "11px",
  color: "#e8e8f2",
  boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
};

/* ── Stat Card ─────────────────────────────────────────── */
function StatCard({
  icon,
  label,
  value,
  sub,
  color = "#7c3aed",
  delay = 0,
}: {
  icon: string;
  label: string;
  value: string | number;
  sub?: string;
  color?: string;
  delay?: number;
}) {
  return (
    <div className="card-shell animate-fade-in" style={{ borderRadius: "24px", animationDelay: `${delay}ms` }}>
      <div className="card-core" style={{ borderRadius: "19px", padding: "20px" }}>
        {/* Icon */}
        <div
          style={{
            width: "36px",
            height: "36px",
            borderRadius: "12px",
            background: `${color}15`,
            border: `1px solid ${color}30`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "16px",
            marginBottom: "16px",
          }}
        >
          {icon}
        </div>

        {/* Value */}
        <div
          style={{
            fontSize: "26px",
            fontWeight: 800,
            letterSpacing: "-0.03em",
            color: "#e8e8f2",
            fontFamily: "var(--font-mono)",
            marginBottom: "4px",
          }}
        >
          {value}
        </div>

        {/* Label */}
        <div style={{ fontSize: "11px", color: "rgba(100,116,139,0.8)", fontWeight: 500 }}>{label}</div>

        {/* Sub */}
        {sub && (
          <div style={{ fontSize: "10px", color: "#334155", marginTop: "4px" }}>{sub}</div>
        )}
      </div>
    </div>
  );
}

/* ── Chart Card ─────────────────────────────────────────── */
function ChartCard({ title, children, delay = 0 }: { title: string; children: React.ReactNode; delay?: number }) {
  return (
    <div className="card-shell animate-fade-in" style={{ borderRadius: "24px", animationDelay: `${delay}ms` }}>
      <div className="card-core" style={{ borderRadius: "19px", padding: "24px" }}>
        <h2
          style={{
            fontSize: "13px",
            fontWeight: 700,
            color: "#e8e8f2",
            letterSpacing: "-0.01em",
            marginBottom: "20px",
          }}
        >
          {title}
        </h2>
        {children}
      </div>
    </div>
  );
}

/* ── Analytics Page ─────────────────────────────────────── */
export default function AnalyticsPage() {
  const [stats, setStats] = useState<PipelineStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reloadStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const freshStats = await fetchStats();
      setStats(freshStats);
    } catch (e: any) {
      setError(e?.message ?? "Failed to load analytics.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { reloadStats(); }, []);

  /* ── Loading ── */
  if (loading) {
    return (
      <div style={{ maxWidth: "1280px", margin: "0 auto", padding: "48px 24px" }}>
        <div style={{ marginBottom: "48px" }}>
          <div className="shimmer" style={{ height: "12px", width: "120px", borderRadius: "999px", marginBottom: "20px" }} />
          <div className="shimmer" style={{ height: "40px", width: "320px", borderRadius: "8px", marginBottom: "12px" }} />
          <div className="shimmer" style={{ height: "14px", width: "240px", borderRadius: "6px" }} />
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: "16px" }}>
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="card-shell" style={{ borderRadius: "24px" }}>
              <div className="card-core" style={{ borderRadius: "19px", padding: "20px" }}>
                <div className="shimmer" style={{ height: "36px", width: "36px", borderRadius: "12px", marginBottom: "16px" }} />
                <div className="shimmer" style={{ height: "24px", width: "80px", borderRadius: "6px", marginBottom: "8px" }} />
                <div className="shimmer" style={{ height: "10px", width: "100px", borderRadius: "4px" }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  /* ── Error ── */
  const isBackendDown = Boolean(
    error && /503|Service unavailable|ECONNRESET|network|failed to fetch/i.test(error)
  );

  if (error || !stats) {
    return (
      <div style={{ maxWidth: "1280px", margin: "0 auto", padding: "48px 24px" }}>
        <div className="card-shell animate-fade-in" style={{ borderRadius: "28px", maxWidth: "560px", margin: "0 auto" }}>
          <div
            className="card-core"
            style={{
              borderRadius: "23px",
              padding: "56px 40px",
              textAlign: "center",
              borderColor: "rgba(0,212,255,0.12)",
            }}
          >
            <div
              style={{
                width: "56px",
                height: "56px",
                borderRadius: "18px",
                background: "rgba(0,212,255,0.06)",
                border: "1px solid rgba(0,212,255,0.15)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "24px",
                margin: "0 auto 24px",
                color: "#38bdf8",
              }}
            >
              ⊟
            </div>

            <h2
              style={{
                fontSize: "22px",
                fontWeight: 700,
                letterSpacing: "-0.02em",
                color: "#e8e8f2",
                marginBottom: "12px",
              }}
            >
              {isBackendDown ? "Analytics unavailable" : "Couldn't load dashboard"}
            </h2>

            <p style={{ fontSize: "13px", color: "rgba(100,116,139,0.8)", lineHeight: 1.6, marginBottom: "8px" }}>
              {isBackendDown
                ? "The analytics service isn't responding. Start the backend server and retry."
                : "Dashboard data couldn't be fetched. Confirm the backend is running and try again."
              }
            </p>

            {error && (
              <p style={{ fontSize: "11px", color: "#334155", marginBottom: "24px", fontFamily: "var(--font-mono)" }}>
                {error}
              </p>
            )}

            <button
              onClick={reloadStats}
              className="btn-island btn-primary"
            >
              Retry
              <span
                className="btn-island-icon"
                style={{ background: "rgba(0,212,255,0.12)", color: "#00d4ff", width: "28px", height: "28px", fontSize: "12px" }}
              >
                ↻
              </span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  /* ── Data prep ── */
  const sourceData = Object.entries(stats.articles_by_source).map(([name, count]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    count,
  }));

  const categoryData = Object.entries(stats.articles_by_category)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 8)
    .map(([name, value]) => ({ name, value }));

  const dailyData = stats.daily_ingestion.map((d) => ({
    ...d,
    date: new Date(d.date).toLocaleDateString("en-GB", { day: "2-digit", month: "short" }),
  }));

  const dispatchRate =
    stats.total_articles > 0
      ? ((stats.dispatched_count / stats.total_articles) * 100).toFixed(1)
      : "0.0";

  const STAT_CARDS = [
    { icon: "◈", label: "Total Articles",   value: stats.total_articles.toLocaleString(),     color: "#7c3aed" },
    { icon: "✦", label: "Dispatched",       value: stats.dispatched_count.toLocaleString(),   color: "#00d4ff", sub: `${dispatchRate}% dispatch rate` },
    { icon: "⊙", label: "Tokens Spent",     value: stats.total_tokens_spent.toLocaleString(), color: "#f97316" },
    { icon: "$", label: "API Cost",          value: `$${stats.total_cost_usd.toFixed(4)}`,     color: "#10ffa0" },
    { icon: "⊞", label: "Active Sources",   value: Object.keys(stats.articles_by_source).length,  color: "#ec4899" },
    { icon: "⊟", label: "Categories",       value: Object.keys(stats.articles_by_category).length, color: "#14b8a6" },
  ];

  return (
    <div style={{ maxWidth: "1280px", margin: "0 auto", padding: "48px 24px" }}>

      {/* ── Hero ── */}
      <div className="animate-fade-in" style={{ marginBottom: "48px" }}>
        <div className="eyebrow" style={{ marginBottom: "16px" }}>
          <span style={{ fontSize: "8px" }}>⊟</span>
          Pipeline Analytics
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
          Intelligence{" "}
          <span className="gradient-text-green">Dashboard</span>
        </h1>
        <p style={{ fontSize: "14px", color: "rgba(100,116,139,0.9)", lineHeight: 1.6 }}>
          Token spend, ingestion trends, and pipeline performance metrics.
        </p>
      </div>

      {/* ── Stat grid ── */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(170px, 1fr))",
          gap: "16px",
          marginBottom: "32px",
        }}
      >
        {STAT_CARDS.map(({ icon, label, value, color, sub }, i) => (
          <StatCard key={label} icon={icon} label={label} value={value} sub={sub} color={color} delay={i * 60} />
        ))}
      </div>

      {/* ── Charts row 1 ── */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
          gap: "20px",
          marginBottom: "20px",
        }}
      >
        {/* Daily ingestion */}
        <ChartCard title="Daily Ingestion — 14 days" delay={400}>
          {dailyData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={dailyData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="date" stroke="#334155" tick={{ fontSize: 10, fill: "#475569" }} />
                <YAxis stroke="#334155" tick={{ fontSize: 10, fill: "#475569" }} />
                <Tooltip contentStyle={TOOLTIP_STYLE} />
                <Line
                  type="monotone" dataKey="count" stroke={CHART_COLORS.violet}
                  strokeWidth={2} dot={{ fill: CHART_COLORS.violet, r: 3 }} name="Articles"
                />
                <Line
                  type="monotone" dataKey="avg_score" stroke={CHART_COLORS.cyan}
                  strokeWidth={2} dot={{ fill: CHART_COLORS.cyan, r: 3 }} name="Avg Score"
                />
                <Legend wrapperStyle={{ fontSize: "11px", color: "#64748b", paddingTop: "8px" }} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ height: "220px", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", color: "#334155" }}>
              <span style={{ fontSize: "32px", marginBottom: "12px", opacity: 0.4 }}>◎</span>
              <span style={{ fontSize: "12px" }}>No data yet — run the pipeline.</span>
            </div>
          )}
        </ChartCard>

        {/* Articles by source */}
        <ChartCard title="Articles by Source" delay={480}>
          {sourceData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={sourceData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="name" stroke="#334155" tick={{ fontSize: 11, fill: "#475569" }} />
                <YAxis stroke="#334155" tick={{ fontSize: 10, fill: "#475569" }} />
                <Tooltip contentStyle={TOOLTIP_STYLE} />
                <Bar dataKey="count" name="Articles" radius={[6, 6, 0, 0]}>
                  {sourceData.map((_, i) => (
                    <Cell key={i} fill={[CHART_COLORS.violet, CHART_COLORS.cyan, CHART_COLORS.green][i % 3]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ height: "220px", display: "flex", alignItems: "center", justifyContent: "center", color: "#334155", fontSize: "12px" }}>
              No source data available.
            </div>
          )}
        </ChartCard>
      </div>

      {/* ── Charts row 2: Categories ── */}
      <ChartCard title="Articles by Category" delay={560}>
        {categoryData.length > 0 ? (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px", alignItems: "center" }}>
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%" cy="50%"
                  innerRadius={65} outerRadius={105}
                  paddingAngle={3}
                  dataKey="value"
                  strokeWidth={0}
                >
                  {categoryData.map((_, i) => (
                    <Cell key={i} fill={CATEGORY_COLORS[i % CATEGORY_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={TOOLTIP_STYLE} />
              </PieChart>
            </ResponsiveContainer>

            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {categoryData.map(({ name, value }, i) => {
                const total = categoryData.reduce((s, d) => s + d.value, 0);
                const pct = total > 0 ? ((value / total) * 100).toFixed(0) : "0";
                return (
                  <div key={name} style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    <div
                      style={{
                        width: "8px",
                        height: "8px",
                        borderRadius: "50%",
                        flexShrink: 0,
                        background: CATEGORY_COLORS[i % CATEGORY_COLORS.length],
                      }}
                    />
                    <span style={{ fontSize: "11px", color: "rgba(148,163,184,0.85)", flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {name}
                    </span>
                    <span style={{ fontSize: "11px", color: "#475569", fontFamily: "var(--font-mono)", flexShrink: 0 }}>
                      {value} <span style={{ opacity: 0.5 }}>· {pct}%</span>
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <div style={{ height: "240px", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", color: "#334155" }}>
            <span style={{ fontSize: "32px", marginBottom: "12px", opacity: 0.4 }}>◎</span>
            <span style={{ fontSize: "12px" }}>No category data yet.</span>
          </div>
        )}
      </ChartCard>
    </div>
  );
}
