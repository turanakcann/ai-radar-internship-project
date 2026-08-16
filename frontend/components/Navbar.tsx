"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import { triggerPipeline } from "@/lib/api";
import { clsx } from "clsx";

const NAV_LINKS = [
  { href: "/", label: "Feed" },
  { href: "/search", label: "Search" },
  { href: "/analytics", label: "Analytics" },
];

export function Navbar() {
  const pathname = usePathname();
  const [triggering, setTriggering] = useState(false);
  const [triggerMsg, setTriggerMsg] = useState<"" | "success" | "error">("");
  const [triggerText, setTriggerText] = useState("");
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  // Collapse on route change
  useEffect(() => { setMenuOpen(false); }, [pathname]);

  // Shrink nav on scroll
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const handleTrigger = async () => {
    setTriggering(true);
    setTriggerMsg("");
    setTriggerText("");
    try {
      const res = await triggerPipeline();
      setTriggerMsg("success");
      setTriggerText(res.status === "started" ? "Pipeline started" : (res.message ?? "Running"));
    } catch (e: any) {
      setTriggerMsg("error");
      setTriggerText(e.message?.slice(0, 40) ?? "Error");
    } finally {
      setTriggering(false);
      setTimeout(() => { setTriggerMsg(""); setTriggerText(""); }, 4000);
    }
  };

  return (
    <>
      {/* ── Floating Island Navbar ─────────────────────────── */}
      <header
        className="fixed top-0 left-0 right-0 flex justify-center px-4"
        style={{ zIndex: 100, paddingTop: scrolled ? "10px" : "18px", transition: "padding 400ms cubic-bezier(0.32,0.72,0,1)" }}
      >
        <nav
          className="glass w-full flex items-center justify-between px-4"
          style={{
            maxWidth: "960px",
            height: "52px",
            borderRadius: "999px",
            backdropFilter: "blur(24px) saturate(180%)",
            WebkitBackdropFilter: "blur(24px) saturate(180%)",
            background: "rgba(10,10,20,0.8)",
            border: "1px solid rgba(255,255,255,0.08)",
            boxShadow: "0 4px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.06)",
            transition: "all 400ms cubic-bezier(0.32,0.72,0,1)",
          }}
        >
          {/* Logo */}
          <Link
            href="/"
            className="flex items-center gap-2.5 shrink-0"
            style={{ textDecoration: "none" }}
          >
            <div
              style={{
                width: "30px",
                height: "30px",
                borderRadius: "10px",
                background: "linear-gradient(135deg, #7c3aed 0%, #00d4ff 100%)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: "0 0 12px rgba(124,58,237,0.4)",
                fontSize: "14px",
                transition: "transform 400ms cubic-bezier(0.32,0.72,0,1)",
              }}
              onMouseEnter={e => (e.currentTarget.style.transform = "scale(1.1) rotate(-5deg)")}
              onMouseLeave={e => (e.currentTarget.style.transform = "scale(1) rotate(0deg)")}
            >
              ◈
            </div>
            <span style={{ fontWeight: 700, fontSize: "14px", letterSpacing: "-0.02em", color: "#e8e8f2" }}>
              Davision{" "}
              <span className="gradient-text-cyan">Radar</span>
            </span>
          </Link>

          {/* Desktop Nav Links */}
          <div className="hidden sm:flex items-center gap-1">
            {NAV_LINKS.map(({ href, label }) => {
              const active = pathname === href;
              return (
                <Link
                  key={href}
                  href={href}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    padding: "6px 14px",
                    borderRadius: "999px",
                    fontSize: "13px",
                    fontWeight: active ? 600 : 400,
                    color: active ? "#c4b5fd" : "rgba(148,163,184,0.8)",
                    background: active ? "rgba(124,58,237,0.15)" : "transparent",
                    border: active ? "1px solid rgba(124,58,237,0.3)" : "1px solid transparent",
                    textDecoration: "none",
                    transition: "all 300ms cubic-bezier(0.32,0.72,0,1)",
                  }}
                  onMouseEnter={e => { if (!active) { (e.currentTarget as HTMLElement).style.color = "#e8e8f2"; (e.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.05)"; } }}
                  onMouseLeave={e => { if (!active) { (e.currentTarget as HTMLElement).style.color = "rgba(148,163,184,0.8)"; (e.currentTarget as HTMLElement).style.background = "transparent"; } }}
                >
                  {label}
                </Link>
              );
            })}
          </div>

          {/* Right Controls */}
          <div className="flex items-center gap-3">
            {/* Feedback message */}
            {triggerMsg && (
              <span
                className="animate-fade-in hidden sm:block"
                style={{
                  fontSize: "11px",
                  fontWeight: 500,
                  color: triggerMsg === "success" ? "#10ffa0" : "#f87171",
                  whiteSpace: "nowrap",
                }}
              >
                {triggerText}
              </span>
            )}

            {/* Run Pipeline — Button-in-Button with pulse ring */}
            <div style={{ position: "relative" }}>
              {triggering && (
                <span
                  style={{
                    position: "absolute",
                    inset: 0,
                    borderRadius: "999px",
                    border: "1px solid rgba(0,212,255,0.5)",
                    animation: "pulse-ring 1.6s cubic-bezier(0.215,0.61,0.355,1) infinite",
                    pointerEvents: "none",
                  }}
                />
              )}
              <button
                onClick={handleTrigger}
                disabled={triggering}
                className="btn-island btn-primary"
                style={{ fontSize: "12px", padding: "7px 14px 7px 16px" }}
                aria-label="Run intelligence pipeline"
              >
                <span style={{ color: triggering ? "rgba(232,232,242,0.5)" : "#e8e8f2" }}>
                  {triggering ? "Running…" : "Run Pipeline"}
                </span>
                <span
                  className="btn-island-icon"
                  style={{
                    background: triggering ? "rgba(255,255,255,0.05)" : "rgba(0,212,255,0.12)",
                    fontSize: "11px",
                    color: "#00d4ff",
                  }}
                >
                  {triggering ? "↻" : "⚡"}
                </span>
              </button>
            </div>

            {/* Mobile hamburger */}
            <button
              className="sm:hidden flex flex-col justify-center items-center w-8 h-8 gap-1 relative"
              onClick={() => setMenuOpen(v => !v)}
              aria-label={menuOpen ? "Close menu" : "Open menu"}
              style={{ background: "transparent", border: "none", cursor: "pointer" }}
            >
              <span
                style={{
                  display: "block",
                  width: "18px",
                  height: "1.5px",
                  background: "#e8e8f2",
                  transformOrigin: "center",
                  transition: "transform 300ms cubic-bezier(0.32,0.72,0,1), opacity 200ms",
                  transform: menuOpen ? "rotate(45deg) translateY(4px)" : "none",
                }}
              />
              <span
                style={{
                  display: "block",
                  width: "18px",
                  height: "1.5px",
                  background: "#e8e8f2",
                  transition: "opacity 200ms",
                  opacity: menuOpen ? 0 : 1,
                }}
              />
              <span
                style={{
                  display: "block",
                  width: "18px",
                  height: "1.5px",
                  background: "#e8e8f2",
                  transformOrigin: "center",
                  transition: "transform 300ms cubic-bezier(0.32,0.72,0,1)",
                  transform: menuOpen ? "rotate(-45deg) translateY(-4px)" : "none",
                }}
              />
            </button>
          </div>
        </nav>
      </header>

      {/* ── Mobile Menu Overlay ────────────────────────────── */}
      {menuOpen && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 99,
            backdropFilter: "blur(32px) saturate(180%)",
            WebkitBackdropFilter: "blur(32px) saturate(180%)",
            background: "rgba(5,5,8,0.90)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            gap: "8px",
          }}
        >
          {NAV_LINKS.map(({ href, label }, i) => (
            <Link
              key={href}
              href={href}
              className="animate-fade-in"
              style={{
                animationDelay: `${i * 60 + 80}ms`,
                fontSize: "28px",
                fontWeight: 700,
                color: pathname === href ? "#c4b5fd" : "rgba(232,232,242,0.7)",
                textDecoration: "none",
                letterSpacing: "-0.02em",
                padding: "12px 32px",
                borderRadius: "16px",
                background: pathname === href ? "rgba(124,58,237,0.12)" : "transparent",
                border: pathname === href ? "1px solid rgba(124,58,237,0.25)" : "1px solid transparent",
                transition: "all 300ms cubic-bezier(0.32,0.72,0,1)",
              }}
            >
              {label}
            </Link>
          ))}
        </div>
      )}

      {/* Spacer so content doesn't hide under fixed navbar */}
      <div style={{ height: "80px" }} />
    </>
  );
}
