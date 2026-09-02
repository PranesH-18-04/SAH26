# SIH26145 — AI-Based Detection of Cyber Threats in Unidirectional IP Traffic (Basic Demo)

**Problem Statement:** SIH26145 (NTRO) — detect cyber threats using AI/ML from
network traffic that flows in one direction only (passive, read-only monitoring).

This repo is a **college selection-round demo**. It simulates the concept
end-to-end without needing real network hardware or a data diode.

## Architecture

```
Synthetic traffic generator (simulates unidirectional flow)
        |
        v
Feature extractor (packet size, rate, port, protocol)
        |
        v
Detector: Rule-based checks  +  Isolation Forest (ML anomaly detection)
        |
        v
Alert stream (FastAPI + WebSocket)
        |
        v
React dashboard (live alert table)
```

See `docs/architecture.png` for a visual diagram.

## What's implemented (this round)

- Synthetic traffic generator with 4 patterns: normal, port scan, DDoS burst, unusual packet size
- Feature extraction from raw flow records
- Two-layer detection: simple threshold rules + Isolation Forest anomaly model
- FastAPI backend exposing REST + WebSocket alert stream
- React dashboard showing live alerts as they're detected
- LLM-based (Gemini) plain-language summary attached to each alert, with a
  safe fallback if no key is configured

## What's NOT implemented yet (planned for later rounds)

- Real packet capture / integration with actual network taps
- Persistent storage (currently in-memory only)
- LLM-based plain-language explanation of alerts
- Throughput/latency benchmarking at scale
- Authentication / role-based access on the dashboard

## How to run locally

**Backend:**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then paste your real Gemini API key into .env
uvicorn main:app --reload
```
Backend runs at `http://localhost:8000`.

> **Note:** If no API key is set in `.env`, the app still works — alerts just
> fall back to a plain templated summary instead of an AI-generated one. This
> means the demo never breaks in front of judges even if the key is missing
> or the quota runs out.

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at `http://localhost:5173`.

Click **"Start Traffic Replay"** on the dashboard to simulate live traffic and
watch alerts appear in real time.

## Why this design fits the problem statement

The system never sends anything back into the "source" — it only ingests
flow data and emits alerts outward, mirroring the read-only nature of a
unidirectional/data-diode link described in the problem statement. Detection
combines transparent rules (explainable, fast) with an ML layer (catches
anomalies rules don't cover), matching the "AI-based" requirement while
staying lightweight enough for a 36-hour build.

## Team

_Add your team name / members here._
