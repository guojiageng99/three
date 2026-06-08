# Presentation Enhancements Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the approved presentation-oriented enhancements for the Generative Agents demo, covering structured timeline data, retrieval explanations, knowledge spread visibility, speed control, and snapshot save/load.

**Architecture:** Extend the backend world-state schema first so the frontend can remain a thin renderer of authoritative simulation state. Add narrowly scoped HTTP control endpoints for speed and snapshot actions, then layer new panels and controls into the existing single-page frontend layout without changing the core page structure.

**Tech Stack:** FastAPI, Pydantic, Python threading, Next.js, React, TypeScript, CSS

---

### Task 1: Extend backend models for presentation state

**Files:**
- Modify: `backend/app/models.py`
- Test: `backend/tests/test_models.py`

**Step 1: Write the failing test**

```python
from app.models import EventLog, KnowledgeEdge, RetrievalExplanation, SnapshotStatus, WorldState


def test_world_state_supports_presentation_fields():
    event = EventLog(
        id="evt-1",
        time="10:00",
        title="Party invitation shared",
        detail="Alice tells Bob about the gathering.",
        event_type="share",
        actor_ids=["alice", "bob"],
        location_id="cafe",
        tick_count=4,
    )
    explanation = RetrievalExplanation(
        memory_id="mem-1",
        total_score=0.82,
        importance_score=0.36,
        recency_score=0.20,
        location_bonus=0.18,
        social_bonus=0.08,
        keyword_overlap_count=3,
        explanation_tags=["recent", "same location"],
    )
    edge = KnowledgeEdge(source_agent_id="alice", target_agent_id="bob", learned_at="10:00", tick_count=4)
    snapshot = SnapshotStatus(exists=True, label="10:00", tick_count=4)

    state = WorldState(
        day_label="2026-06-04",
        time_label="10:00",
        running=False,
        tick_count=4,
        llm_enabled=False,
        locations=[],
        agents=[],
        events=[event],
        knowledge_edges=[edge],
        knowledge_status={"alice": "08:00", "bob": "10:00"},
        active_speed_label="1x",
        available_speed_labels=["0.5x", "1x", "2x"],
        snapshot_status=snapshot,
    )

    assert state.events[0].event_type == "share"
    assert state.knowledge_edges[0].target_agent_id == "bob"
    assert state.snapshot_status.exists is True
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_models.py::test_world_state_supports_presentation_fields -v`
Expected: FAIL because the new model fields do not exist yet.

**Step 3: Write minimal implementation**

Add the following model structures:

- `RetrievalExplanation`
- `KnowledgeEdge`
- `SnapshotStatus`
- new fields on `Agent` for retrieval explanations
- new fields on `EventLog` for structured event metadata
- new fields on `WorldState` for knowledge state, speed state, and snapshot state

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_models.py::test_world_state_supports_presentation_fields -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/models.py backend/tests/test_models.py
git commit -m "feat: extend backend models for presentation state"
```

### Task 2: Add retrieval explanation support in cognition

**Files:**
- Modify: `backend/app/cognition.py`
- Modify: `backend/app/models.py`
- Test: `backend/tests/test_cognition.py`

**Step 1: Write the failing test**

```python
from app.cognition import AgentCognition


def test_retrieve_memories_returns_score_breakdown(sample_agent, sample_location, sample_plan, nearby_agents):
    cognition = AgentCognition()

    memories, explanations = cognition.retrieve_memories_with_explanations(
        agent=sample_agent,
        active_plan=sample_plan,
        current_location=sample_location,
        nearby_agents=nearby_agents,
        time_label="10:00",
        limit=3,
    )

    assert len(memories) == len(explanations)
    assert explanations[0].memory_id == memories[0].id
    assert explanations[0].total_score > 0
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_cognition.py::test_retrieve_memories_returns_score_breakdown -v`
Expected: FAIL because the helper method and explanation output do not exist yet.

**Step 3: Write minimal implementation**

Implement a retrieval helper that:

- computes the same ranking as the current retrieval logic
- returns retrieved memories
- returns structured score breakdown data for each selected memory
- derives compact explanation tags from dominant score components

Keep the existing retrieval behavior intact by having `retrieve_memories()` call the new helper internally if that reduces duplication.

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_cognition.py::test_retrieve_memories_returns_score_breakdown -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/cognition.py backend/app/models.py backend/tests/test_cognition.py
git commit -m "feat: add retrieval score explanations"
```

### Task 3: Extend simulation engine with structured events and knowledge spread tracking

**Files:**
- Modify: `backend/app/simulation.py`
- Modify: `backend/app/models.py`
- Test: `backend/tests/test_simulation_events.py`

**Step 1: Write the failing test**

```python
from app.simulation import SimulationEngine


def test_knowledge_share_creates_structured_event_and_edge():
    engine = SimulationEngine()
    engine.tick()
    engine.tick()
    engine.tick()
    engine.tick()

    share_events = [event for event in engine.snapshot().events if event.event_type == "share"]
    assert share_events
    assert engine.snapshot().knowledge_edges
    assert engine.snapshot().knowledge_status["bob"] == "10:00"
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_simulation_events.py::test_knowledge_share_creates_structured_event_and_edge -v`
Expected: FAIL because structured event fields and knowledge tracking are not implemented.

**Step 3: Write minimal implementation**

Update the engine to:

- emit structured events for move, conversation/share, reflection, and system events
- record first-known timestamps in `knowledge_status`
- append propagation edges when a listener learns the gathering
- expose these fields in `snapshot()`

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_simulation_events.py::test_knowledge_share_creates_structured_event_and_edge -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/simulation.py backend/app/models.py backend/tests/test_simulation_events.py
git commit -m "feat: track structured events and knowledge spread"
```

### Task 4: Add speed control and snapshot backend APIs

**Files:**
- Modify: `backend/app/simulation.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_simulation_controls.py`
- Test: `backend/tests/test_api_controls.py`

**Step 1: Write the failing tests**

```python
from app.simulation import SimulationEngine


def test_set_speed_updates_active_label():
    engine = SimulationEngine()
    engine.set_speed("2x")
    assert engine.snapshot().active_speed_label == "2x"


def test_snapshot_save_and_load_restores_tick_count():
    engine = SimulationEngine()
    engine.tick()
    engine.tick()
    engine.save_snapshot()
    engine.tick()
    engine.load_snapshot()
    assert engine.snapshot().tick_count == 2
    assert engine.snapshot().running is False
```

```python
from fastapi.testclient import TestClient
from app.main import app


def test_speed_endpoint_updates_speed():
    client = TestClient(app)
    response = client.post("/api/sim/speed", json={"speed_label": "2x"})
    assert response.status_code == 200
    assert response.json()["active_speed_label"] == "2x"
```

**Step 2: Run tests to verify they fail**

Run: `pytest backend/tests/test_simulation_controls.py backend/tests/test_api_controls.py -v`
Expected: FAIL because speed and snapshot controls do not exist.

**Step 3: Write minimal implementation**

Add:

- speed presets in the engine
- `set_speed()` with validation
- snapshot save/load helpers using deep copies
- HTTP endpoints for speed and snapshot operations

Use simple request models in `backend/app/main.py` for JSON body validation.

**Step 4: Run tests to verify they pass**

Run: `pytest backend/tests/test_simulation_controls.py backend/tests/test_api_controls.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/simulation.py backend/app/main.py backend/tests/test_simulation_controls.py backend/tests/test_api_controls.py
git commit -m "feat: add speed and snapshot controls"
```

### Task 5: Extend frontend types and API helpers

**Files:**
- Modify: `frontend/lib/types.ts`
- Modify: `frontend/lib/api.ts`
- Test: `frontend` type-check via `npm run build`

**Step 1: Write the failing integration check**

No standalone test file is required here. The contract check is the TypeScript build.

**Step 2: Run build to verify it fails after backend-oriented type usage is introduced**

Run: `cd frontend && npm run build`
Expected: FAIL until the frontend type layer is updated.

**Step 3: Write minimal implementation**

Update frontend types to include:

- structured event fields
- retrieval explanations
- knowledge spread data
- speed labels
- snapshot status

Add API helpers for:

- speed update
- snapshot save
- snapshot load

Preserve the existing `postAction()` helper for simple POST endpoints.

**Step 4: Run build to verify it passes**

Run: `cd frontend && npm run build`
Expected: PASS

**Step 5: Commit**

```bash
git add frontend/lib/types.ts frontend/lib/api.ts
git commit -m "feat: add frontend types for presentation state"
```

### Task 6: Add presentation controls to the frontend

**Files:**
- Modify: `frontend/components/Controls.tsx`
- Modify: `frontend/app/page.tsx`
- Modify: `frontend/app/globals.css`
- Test: `frontend` build and manual browser check

**Step 1: Write the failing integration check**

Use the build as the contract check after adding new props and control actions.

**Step 2: Run build to verify it fails**

Run: `cd frontend && npm run build`
Expected: FAIL until the new control props and handlers are wired correctly.

**Step 3: Write minimal implementation**

Extend controls to support:

- speed selection buttons
- snapshot save button
- snapshot load button
- disabled state for load when no snapshot exists

Wire the actions from `page.tsx` through the API helpers and let WebSocket state remain authoritative for UI refresh.

**Step 4: Run build to verify it passes**

Run: `cd frontend && npm run build`
Expected: PASS

**Step 5: Commit**

```bash
git add frontend/components/Controls.tsx frontend/app/page.tsx frontend/app/globals.css
git commit -m "feat: add presentation controls to frontend"
```

### Task 7: Add timeline, spread, and retrieval explanation panels

**Files:**
- Modify: `frontend/components/Sidebar.tsx`
- Modify: `frontend/app/page.tsx`
- Modify: `frontend/app/globals.css`
- Test: `frontend` build and manual browser check

**Step 1: Write the failing integration check**

Use the frontend build as the first contract check after adding new fields to the sidebar props and render paths.

**Step 2: Run build to verify it fails**

Run: `cd frontend && npm run build`
Expected: FAIL until the new panel data is typed and rendered correctly.

**Step 3: Write minimal implementation**

Add panels for:

- structured event timeline
- knowledge spread status and propagation chain
- retrieval explanation details beside retrieved memories
- snapshot status summary in the world-state area

Keep the existing selected-agent, plan, recent memories, reflections, and event log sections if still useful; remove duplication only if the new panels fully replace the old information.

**Step 4: Run build to verify it passes**

Run: `cd frontend && npm run build`
Expected: PASS

**Step 5: Commit**

```bash
git add frontend/components/Sidebar.tsx frontend/app/page.tsx frontend/app/globals.css
git commit -m "feat: add presentation insight panels"
```

### Task 8: Verify end-to-end behavior and update README if needed

**Files:**
- Modify: `README.md`
- Test: `backend/tests/*.py`
- Test: `frontend` build

**Step 1: Run the backend test suite**

Run: `pytest backend/tests -v`
Expected: PASS

**Step 2: Run the frontend production build**

Run: `cd frontend && npm run build`
Expected: PASS

**Step 3: Run a manual smoke check**

Verify:

- `Reset` returns to the opening state
- speed controls update the world-state display
- snapshot save/load works and load resumes in paused mode
- timeline distinguishes move, share, and reflection events
- propagation state shows `Alice -> Bob -> Carol`
- retrieval explanations render for the selected agent

**Step 4: Update README if the new controls need documentation**

Add only the minimum usage notes required for speed and snapshot controls.

**Step 5: Commit**

```bash
git add README.md backend/tests frontend
git commit -m "docs: document presentation controls"
```
