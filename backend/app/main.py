from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)

from .cognition import LlmGenerationError
from .simulation import engine

app = FastAPI(title="Generative Agents Demo API")


class SpeedRequest(BaseModel):
    speed_label: str


class BookmarkRequest(BaseModel):
    bookmark_key: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _handle_llm_errors(action) -> dict:
    try:
        return action()
    except LlmGenerationError as exc:
        raise HTTPException(
            status_code=502,
            detail={"status": exc.status, "message": exc.message},
        ) from exc


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
    def run() -> dict:
        engine.tick()
        return {"ok": True, "tick_count": engine.snapshot().tick_count}

    return _handle_llm_errors(run)


@app.post("/api/sim/reset")
def reset_simulation() -> dict:
    def run() -> dict:
        engine.reset()
        return {"ok": True}

    return _handle_llm_errors(run)


@app.post("/api/sim/speed")
def set_simulation_speed(payload: SpeedRequest) -> dict:
    active_speed_label = engine.set_speed(payload.speed_label)
    return {
        "ok": True,
        "active_speed_label": active_speed_label,
        "available_speed_labels": engine.snapshot().available_speed_labels,
    }


@app.post("/api/sim/snapshot/save")
def save_simulation_snapshot() -> dict:
    snapshot_status = engine.save_snapshot()
    return {
        "ok": True,
        "snapshot_status": snapshot_status.model_dump(),
    }


@app.post("/api/sim/snapshot/load")
def load_simulation_snapshot() -> dict:
    snapshot_status = engine.load_snapshot()
    return {
        "ok": True,
        "running": False,
        "snapshot_status": snapshot_status.model_dump(),
    }


@app.post("/api/sim/bookmark")
def jump_to_bookmark(payload: BookmarkRequest) -> dict:
    def run() -> dict:
        bookmark = engine.jump_to_bookmark(payload.bookmark_key)
        return {
            "ok": True,
            "bookmark": bookmark.model_dump(),
        }

    return _handle_llm_errors(run)


@app.websocket("/ws/state")
async def websocket_state(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(engine.snapshot().model_dump())
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        return
