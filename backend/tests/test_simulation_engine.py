from fastapi.testclient import TestClient

from app.cognition import DEFAULT_BAILIAN_BASE_URL, DEFAULT_BAILIAN_MODEL, AgentCognition
from app.main import app
from app.simulation import SimulationEngine


def test_initial_state_only_alice_knows_party() -> None:
    engine = SimulationEngine()
    snapshot = engine.snapshot()

    aware_agents = [agent.id for agent in snapshot.agents if agent.knows_party]

    assert aware_agents == ["alice"]
    assert snapshot.simulation_mode == "deterministic"
    assert snapshot.memory_stream_count == 3
    assert snapshot.reflection_trigger_reason is None


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
    assert snapshot.knowledge_edges[0].source_agent_id == "alice"
    assert snapshot.knowledge_edges[0].target_agent_id == "bob"


def test_second_share_reaches_carol_before_reflection() -> None:
    engine = SimulationEngine()
    for _ in range(12):
        engine.tick()

    snapshot = engine.snapshot()

    assert snapshot.time_label == "14:00"
    assert "carol" in snapshot.knowledge_status
    assert [(edge.source_agent_id, edge.target_agent_id) for edge in snapshot.knowledge_edges] == [
        ("alice", "bob"),
        ("bob", "carol"),
    ]
    assert all(not agent.reflections for agent in snapshot.agents)


def test_reflection_uses_importance_threshold_after_shared_knowledge() -> None:
    engine = SimulationEngine()
    for _ in range(13):
        engine.tick()

    snapshot = engine.snapshot()

    assert snapshot.time_label == "14:30"
    assert snapshot.reflection_trigger_reason is not None
    assert "memory importance crossed" in snapshot.reflection_trigger_reason
    assert all(agent.reflections for agent in snapshot.agents)
    assert snapshot.memory_stream_count > 3


def test_retrieval_exposes_relevance_score() -> None:
    engine = SimulationEngine()
    alice = next(agent for agent in engine.agents if agent.id == "alice")
    retrieved, explanations = engine._cognition.retrieve_memories_with_explanations(
        agent=alice,
        active_plan=alice.active_plan,
        current_location=engine._location(alice.current_location_id),
        nearby_agents=[],
        time_label="08:00",
    )

    assert retrieved
    assert explanations[0].relevance_score >= 0


def test_speed_endpoint_updates_active_speed() -> None:
    client = TestClient(app)

    response = client.post("/api/sim/speed", json={"speed_label": "2x"})

    assert response.status_code == 200
    assert response.json()["active_speed_label"] == "2x"


def test_state_endpoint_exposes_mode_and_memory_fields() -> None:
    client = TestClient(app)

    response = client.get("/api/state")
    payload = response.json()

    assert response.status_code == 200
    assert payload["simulation_mode"] in {"deterministic", "llm"}
    assert "memory_stream_count" in payload
    assert "last_llm_call_status" in payload


def test_bailian_defaults_and_dashscope_key_alias(monkeypatch) -> None:
    monkeypatch.setenv("SIMULATION_MODE", "llm")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setenv("DASHSCOPE_API_KEY", "dashscope-test-key")

    cognition = AgentCognition()

    assert cognition.enabled is True
    assert cognition.api_key == "dashscope-test-key"
    assert cognition.base_url == DEFAULT_BAILIAN_BASE_URL
    assert cognition.model == DEFAULT_BAILIAN_MODEL
    assert cognition.provider == "aliyun-bailian"
    assert cognition.last_llm_call_status == "ready"


def test_snapshot_exposes_bailian_provider_and_model(monkeypatch) -> None:
    monkeypatch.setenv("SIMULATION_MODE", "deterministic")
    engine = SimulationEngine()
    monkeypatch.setenv("SIMULATION_MODE", "llm")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.setenv("DASHSCOPE_API_KEY", "dashscope-test-key")
    engine.simulation_mode = "llm"
    engine._cognition = AgentCognition()

    snapshot = engine.snapshot()

    assert snapshot.llm_provider == "aliyun-bailian"
    assert snapshot.llm_model == "qwen-plus"


def test_llm_action_prompt_uses_selected_agent_private_context(monkeypatch) -> None:
    monkeypatch.setenv("SIMULATION_MODE", "deterministic")
    engine = SimulationEngine()
    bob = next(agent for agent in engine.agents if agent.id == "bob")
    alice = next(agent for agent in engine.agents if agent.id == "alice")
    alice.memory_bank.insert(
        0,
        engine._memory(
            "observation",
            "Alice keeps a private guest list that Bob has not learned.",
            "08:00",
            "home_alice",
            0.9,
        ),
    )

    monkeypatch.setenv("SIMULATION_MODE", "llm")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    cognition = AgentCognition()
    captured_payload = {}

    def fake_chat_json(system_prompt: str, user_payload: dict) -> dict:
        captured_payload.update(user_payload)
        return {"summary": "Bob writes notes at the park.", "utterance": "I should keep observing the town."}

    monkeypatch.setattr(cognition, "_chat_json", fake_chat_json)

    cognition.generate_action(
        agent=bob,
        active_plan=bob.active_plan,
        current_location=engine._location(bob.current_location_id),
        nearby_agents=[],
        retrieved_memories=bob.memory_bank,
        time_label="08:00",
    )

    assert captured_payload["agent"]["name"] == "Bob"
    assert "private guest list" not in " ".join(captured_payload["retrieved_memories"])
    assert "Do not invent hidden memories" in captured_payload["instruction"]


def test_bookmark_jump_matches_reflection_demo_state() -> None:
    engine = SimulationEngine()

    bookmark = engine.jump_to_bookmark("reflection")
    snapshot = engine.snapshot()

    assert bookmark.target_time == "14:30"
    assert snapshot.time_label == "14:30"
    assert all(agent.knows_party for agent in snapshot.agents)
    assert all(agent.reflections for agent in snapshot.agents)


def test_llm_mode_falls_back_when_request_fails(monkeypatch) -> None:
    monkeypatch.setenv("SIMULATION_MODE", "deterministic")
    engine = SimulationEngine()
    monkeypatch.setenv("SIMULATION_MODE", "llm")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_BASE_URL", "http://127.0.0.1:9/v1")
    cognition = AgentCognition()
    agent = next(item for item in engine.agents if item.id == "alice")

    decision = cognition.generate_action(
        agent=agent,
        active_plan=agent.active_plan,
        current_location=engine._location(agent.current_location_id),
        nearby_agents=[],
        retrieved_memories=agent.memory_bank,
        time_label="08:00",
    )

    assert decision.summary
    assert cognition.last_llm_call_status.startswith("error:")


def test_llm_mode_falls_back_when_api_key_missing(monkeypatch) -> None:
    monkeypatch.setenv("SIMULATION_MODE", "deterministic")
    engine = SimulationEngine()
    monkeypatch.setenv("SIMULATION_MODE", "llm")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    cognition = AgentCognition()
    agent = next(item for item in engine.agents if item.id == "alice")

    decision = cognition.generate_action(
        agent=agent,
        active_plan=agent.active_plan,
        current_location=engine._location(agent.current_location_id),
        nearby_agents=[],
        retrieved_memories=agent.memory_bank,
        time_label="08:00",
    )

    assert decision.summary
    assert cognition.enabled is False
    assert cognition.last_llm_call_status == "disabled: missing_api_key"
