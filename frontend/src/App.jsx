import React, { useEffect, useState } from "react";
import AlertTable from "./components/AlertTable.jsx";

const API_BASE = "http://localhost:8000";

export default function App() {
  const [alerts, setAlerts] = useState([]);
  const [status, setStatus] = useState("idle");

  useEffect(() => {
    const ws = new WebSocket(`${API_BASE.replace("http", "ws")}/ws/alerts`);
    ws.onmessage = (event) => {
      const alert = JSON.parse(event.data);
      setAlerts((prev) => [alert, ...prev].slice(0, 100));
    };
    return () => ws.close();
  }, []);

  const startReplay = async () => {
    setStatus("running");
    await fetch(`${API_BASE}/start-replay`, { method: "POST" });
  };

  return (
    <div style={{ fontFamily: "sans-serif", padding: "2rem", maxWidth: 900, margin: "0 auto" }}>
      <h1>SIH26145 — Unidirectional Traffic Threat Detector</h1>
      <p>Basic demo: synthetic traffic replay + rule-based &amp; ML anomaly detection.</p>

      <button onClick={startReplay} disabled={status === "running"}>
        {status === "running" ? "Replay running..." : "Start Traffic Replay"}
      </button>

      <h2 style={{ marginTop: "2rem" }}>Live Alerts ({alerts.length})</h2>
      <AlertTable alerts={alerts} />
    </div>
  );
}
