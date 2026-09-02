"""
main.py
FastAPI backend for SIH26145 basic demo.

Endpoints:
  GET  /                -> health check
  POST /start-replay    -> starts replaying synthetic traffic in background
  GET  /alerts          -> list of alerts detected so far
  WS   /ws/alerts        -> live alert stream
"""

import asyncio
import threading
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from traffic_simulator import generate_dataset, replay_stream
from detector import detect, load_model, train_model
from summarizer import summarize_alert

app = FastAPI(title="SIH26145 - Unidirectional Traffic Threat Detector (Basic Demo)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # fine for a college demo; restrict in real deployments
    allow_methods=["*"],
    allow_headers=["*"],
)

alerts_log = []
connected_clients = []
model = load_model()

if model is None:
    # Auto-train a quick model on startup if none exists, so demo works out of the box
    training_data = generate_dataset(n_normal=300, n_attacks=0)
    model = train_model(training_data)


@app.get("/")
def health():
    return {"status": "ok", "service": "SIH26145 basic demo"}


@app.get("/alerts")
def get_alerts():
    return {"count": len(alerts_log), "alerts": alerts_log[-100:]}


async def broadcast_alert(alert: dict):
    for ws in connected_clients:
        try:
            await ws.send_json(alert)
        except Exception:
            pass


def replay_and_detect():
    """Runs in a background thread: replays synthetic flows and detects threats."""
    dataset = generate_dataset(n_normal=40, n_attacks=15)
    loop = asyncio.new_event_loop()
    for flow in replay_stream(dataset, delay=0.3):
        alert = detect(flow, model)
        if alert:
            alert["summary"] = summarize_alert(alert)
            alerts_log.append(alert)
            loop.run_until_complete(broadcast_alert(alert))
    loop.close()


@app.post("/start-replay")
def start_replay():
    thread = threading.Thread(target=replay_and_detect, daemon=True)
    thread.start()
    return {"status": "replay started"}


@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()   # keep connection alive
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
