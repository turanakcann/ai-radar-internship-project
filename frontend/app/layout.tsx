import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/Navbar";

export const metadata: Metadata = {
  title: "Davision AI Radar — Autonomous Intelligence Feed",
  description:
    "Autonomous AI & ML intelligence platform. Discover the latest breakthroughs in Computer Vision, LLMs, Edge AI, and more — scored and summarized by AI agents.",
  keywords: ["AI", "Machine Learning", "Computer Vision", "LLM", "Tech Radar", "Davision AI"],
  openGraph: {
    title: "Davision AI Radar",
    description: "Autonomous AI & ML intelligence platform powered by multi-agent intelligence.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-mesh dot-grid antialiased min-h-[100dvh]">
        {/* Fixed ambient orbs — GPU safe, pointer-events none */}
        <div
          className="fixed inset-0 pointer-events-none"
          style={{ zIndex: 0 }}
          aria-hidden="true"
        >
          <div
            style={{
              position: "absolute",
              top: "-10%",
              left: "15%",
              width: "600px",
              height: "600px",
              borderRadius: "50%",
              background: "radial-gradient(circle, rgba(124,58,237,0.12) 0%, transparent 70%)",
              filter: "blur(40px)",
              willChange: "transform",
            }}
          />
          <div
            style={{
              position: "absolute",
              bottom: "5%",
              right: "10%",
              width: "500px",
              height: "500px",
              borderRadius: "50%",
              background: "radial-gradient(circle, rgba(0,212,255,0.08) 0%, transparent 70%)",
              filter: "blur(40px)",
            }}
          />
        </div>

        <Navbar />

        <main className="relative min-h-screen" style={{ zIndex: 1 }}>
          {children}
        </main>
      </body>
    </html>
  );
}
