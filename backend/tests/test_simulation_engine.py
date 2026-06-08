from fastapi.testclient import TestClient

from app.main import app
from app.simulation import SimulationEngine


def test_snapshot_save_and_load_restores_tick_count() -> None:
    engine = SimulationEngine()
    engine.tick()
    engine.tick()
    engine.save_snapshot()
    engine.tick()

    engine.load_snapshot()
    snapshot = engine.snapshot()

    assert snapshot.tick_count == 2
    assert snapshot.running is False
    assert snapshot.snapshot_status.exists is True


def test_knowledge_share_creates_edge() -> None:
    engine = SimulationEngine()
    for _ in range(4):
        engine.tick()

    snapshot = engine.snapshot()
    assert snapshot.knowledge_edges
    assert "bob" in snapshot.knowledge_status


def test_speed_endpoint_updates_active_speed() -> None:
    client = TestClient(app)

    response = client.post("/api/sim/speed", json={"speed_label": "2x"})

    assert response.status_code == 200
    assert response.json()["active_speed_label"] == "2x"
