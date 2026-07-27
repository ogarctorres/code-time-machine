"use client";

import { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const API_URL = "http://localhost:8000";

interface TimelinePoint {
  commit_hash: string;
  date: string;
  author: string;
  lines_of_code: number;
  num_functions: number;
  avg_complexity: number;
}

export default function Home() {
  const [repoUrl, setRepoUrl] = useState("");
  const [filePath, setFilePath] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [timeline, setTimeline] = useState<TimelinePoint[] | null>(null);

  async function handleAnalyze() {
    setLoading(true);
    setError(null);
    setTimeline(null);

    try {
      const response = await fetch(`${API_URL}/api/timeline`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_url: repoUrl, file_path: filePath, sample_step: 15 }),
      });

      if (!response.ok) {
        const errBody = await response.json();
        throw new Error(errBody.detail || "Erro ao analisar arquivo");
      }

      const data = await response.json();
      setTimeline(data.timeline);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main
      style={{
        padding: "2rem",
        background: "#0b0f14",
        color: "#e6edf3",
        minHeight: "100vh",
        fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      }}
    >
      <div style={{ marginBottom: "1.5rem" }}>
        <h1 style={{ fontSize: "2rem", marginBottom: "0.2rem" }}>🕰️ Code Time Machine</h1>
        <p style={{ color: "#8b949e", fontSize: "0.95rem" }}>
          Veja a evolução da complexidade de um arquivo Python ao longo de toda sua história.
        </p>
      </div>

      <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap", marginBottom: "1rem" }}>
        <input
          type="text"
          placeholder="https://github.com/org/repo"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          style={inputStyle}
        />
        <input
          type="text"
          placeholder="caminho/do/arquivo.py"
          value={filePath}
          onChange={(e) => setFilePath(e.target.value)}
          style={inputStyle}
        />
        <button onClick={handleAnalyze} disabled={loading} style={buttonStyle(loading)}>
          {loading ? "Analisando..." : "Analisar"}
        </button>
      </div>

      {error && <p style={{ color: "#f85149", marginTop: "1rem" }}>{error}</p>}

      {timeline && (
        <div style={{ background: "#161b22", border: "1px solid #30363d", borderRadius: "8px", padding: "1.5rem", marginTop: "1.5rem" }}>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={timeline}>
              <CartesianGrid stroke="#30363d" />
              <XAxis dataKey="date" tick={{ fill: "#8b949e", fontSize: 11 }} />
              <YAxis tick={{ fill: "#8b949e", fontSize: 11 }} />
              <Tooltip contentStyle={{ background: "#161b22", border: "1px solid #30363d" }} />
              <Legend />
              <Line type="monotone" dataKey="avg_complexity" stroke="#ef4444" name="Complexidade média" strokeWidth={2} />
              <Line type="monotone" dataKey="num_functions" stroke="#22c55e" name="Nº de funções" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </main>
  );
}

const inputStyle = {
  padding: "0.6rem 1rem",
  width: "320px",
  background: "#161b22",
  border: "1px solid #30363d",
  borderRadius: "6px",
  color: "#e6edf3",
  fontSize: "0.9rem",
};

function buttonStyle(loading: boolean) {
  return {
    padding: "0.6rem 1.2rem",
    background: loading ? "#30363d" : "#ef4444",
    color: "#fff",
    border: "none",
    borderRadius: "6px",
    fontWeight: 600,
    cursor: loading ? "not-allowed" : "pointer",
  };
}