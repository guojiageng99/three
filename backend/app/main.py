from __future__ import annotations

import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .simulation import engine

app = FastAPI(title="Generative Agents Demo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
def on_shutdown() -> None:
    engine.shutdown()


@app.get("/api/state")
def get_state() -> dict:
    return engine.snapshot().model_dump()


@app.post("/api/sim/start")
def start_simulation() -> dict:
    engine.start()
    return {"ok": True, "running": True}


@app.post("/api/sim/pause")
def pause_simulation() -> dict:
    engine.pause()
    return {"ok": True, "running": False}


@app.post("/api/sim/tick")
def tick_simulation() -> dict:
    engine.tick()
    return {"ok": True, "tick_count": engine.snapshot().tick_count}


@app.post("/api/sim/reset")
def reset_simulation() -> dict:
    engine.reset()
    return {"ok": True}


@app.websocket("/ws/state")
async def websocket_state(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(engine.snapshot().model_dump())
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        return

