# Report And Video Feature Enrichment Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a small set of low-risk, high-explanation-value features that make the Generative Agents demo easier to defend in a report and easier to narrate in a 10-minute video.

**Architecture:** Build only presentation-facing enhancements on top of the current simulation loop, without redesigning cognition or world logic. Favor features that expose already-existing state more clearly, add one or two deterministic “proof points,” and generate reusable evidence for reports and slides.

**Tech Stack:** FastAPI, Pydantic, Python, Next.js, React, TypeScript, CSS

---

## Why These Features

The current project already covers the core minimum mechanism:

- plan-driven movement
- memory retrieval
- dialogue spread
- reflection generation
- knowledge chain visibility
- snapshot and speed control

What is still missing is not “more AI.”  
What is missing is **more explicit proof material**.

The best remaining additions are the ones that:

1. make one paper mechanism easier to point at on screen
2. create artifacts that can be quoted in the report
3. reduce the amount of explanation the presenter must do from memory
4. do not risk destabilizing the current deterministic demo

The recommended enrichment scope is:

1. `Mechanism checklist panel`
2. `Scenario bookmarks`
3. `Agent relationship / knowledge badges`
4. `Auto-generated evidence export`
5. `Final comparison panel: paper vs demo`

These are chosen because they are:

- easy to justify in the written report
- easy to show in the video
- compatible with the current architecture
- low engineering risk compared with adding new cognition behaviors

---

### Task 1: Add a mechanism checklist panel for live explanation

**Why it matters**

This feature gives the presenter a direct on-screen bridge from “what is happening now” to “which paper mechanism is being demonstrated.”

It improves:

- video narration clarity
- report screenshots with annotations
- defense Q&A resilience

**Files:**
- Modify: `backend/app/models.py`
- Modify: `backend/app/simulation.py`
- Modify: `frontend/lib/types.ts`
- Modify: `frontend/app/page.tsx`
- Modify: `frontend/components/Sidebar.tsx`
- Modify: `frontend/app/globals.css`
- Test: `backend/tests/test_simulation_engine.py`
- Test: `frontend` build via `npm run build`

**Step 1: Write the failing backend test**

```python
from app.simulation import SimulationEngine


def test_snapshot_exposes_mechanism_checklist():
    engine = SimulationEngine()
    state = engine.snapshot()

    assert "planning" in state.mechanism_status
    assert "memory_retrieval" in state.mechanism_status
    assert "dialogue_spread" in state.mechanism_status
    assert "reflection" in state.mechanism_status
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_simulation_engine.py::test_snapshot_exposes_mechanism_checklist -v`  
Expected: FAIL because `mechanism_status` does not exist yet.

**Step 3: Write minimal implementation**

Add a small status structure to world state, for example:

- `planning`
- `movement`
- `memory_retrieval`
- `dialogue_spread`
- `reflection`

Each item should expose a compact label such as:

- `ready`
- `active`
- `completed`
- `not_triggered_yet`

Derive values from the current tick and story state instead of adding a new simulation subsystem.

Render the checklist as a compact panel in the sidebar with one-line explanations.

**Step 4: Run tests and build**

Run:

- `pytest backend/tests/test_simulation_engine.py::test_snapshot_exposes_mechanism_checklist -v`
- `cd frontend && npm run build`

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/models.py backend/app/simulation.py frontend/lib/types.ts frontend/app/page.tsx frontend/components/Sidebar.tsx frontend/app/globals.css backend/tests/test_simulation_engine.py
git commit -m "feat: add mechanism checklist panel"
```

---

### Task 2: Add scenario bookmarks for one-click demo jumps

**Why it matters**

Right now the presenter still has to remember:

- initial state
- first spread state
- second spread state
- reflection state

Scenario bookmarks would let the presenter jump directly to:

- `08:00 初始态`
- `10:00 第一次传播`
- `14:00 第二次传播`
- `14:00+ 反思形成态`

This is one of the highest-value video/demo features because it reduces operator error.

**Files:**
- Modify: `backend/app/models.py`
- Modify: `backend/app/simulation.py`
- Modify: `backend/app/main.py`
- Modify: `frontend/lib/types.ts`
- Modify: `frontend/lib/api.ts`
- Modify: `frontend/components/Controls.tsx`
- Modify: `frontend/app/page.tsx`
- Modify: `frontend/app/globals.css`
- Test: `backend/tests/test_simulation_engine.py`
- Test: `frontend` build via `npm run build`

**Step 1: Write the failing backend test**

```python
from app.simulation import SimulationEngine


def test_jump_to_bookmark_restores_known_demo_state():
    engine = SimulationEngine()
    engine.jump_to_bookmark("first_spread")
    state = engine.snapshot()

    assert state.time_label == "10:00"
    assert state.knowledge_status.get("bob") == "10:00"
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_simulation_engine.py::test_jump_to_bookmark_restores_known_demo_state -v`  
Expected: FAIL because bookmark jumping does not exist.

**Step 3: Write minimal implementation**

Implement a small deterministic bookmark system in the engine:

- `initial`
- `first_spread`
- `second_spread`
- `reflection`

Implementation approach:

- reset the world
- replay deterministic ticks until the target state is reached
- pause after jump

Expose:

- available bookmark labels in `WorldState`
- a simple POST endpoint such as `/api/sim/bookmark`

Add frontend controls as small chips or buttons.

**Step 4: Run tests and build**

Run:

- `pytest backend/tests/test_simulation_engine.py::test_jump_to_bookmark_restores_known_demo_state -v`
- `cd frontend && npm run build`

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/models.py backend/app/simulation.py backend/app/main.py frontend/lib/types.ts frontend/lib/api.ts frontend/components/Controls.tsx frontend/app/page.tsx frontend/app/globals.css backend/tests/test_simulation_engine.py
git commit -m "feat: add scenario bookmarks for demo states"
```

---

### Task 3: Add explicit “who knows what” badges and relationship cues

**Why it matters**

The demo already tracks `knows_party`, but that boolean is not yet used as strongly as it could be in the UI.

Adding stronger knowledge badges and lightweight relationship cues would make propagation easier to narrate:

- who currently knows the gathering
- who learned it recently
- who was told by whom

This is very cheap to implement but very useful for report screenshots.

**Files:**
- Modify: `frontend/components/TownMap.tsx`
- Modify: `frontend/components/Sidebar.tsx`
- Modify: `frontend/app/globals.css`
- Test: `frontend` build via `npm run build`

**Step 1: Write the failing integration check**

Use the frontend production build as the contract check.

**Step 2: Run build to verify it fails after new props are introduced**

Run: `cd frontend && npm run build`  
Expected: FAIL until the new render paths are wired correctly.

**Step 3: Write minimal implementation**

Enhance visual cues:

- add a visible “knows gathering” / “does not know yet” treatment on map chips
- add “recently informed” emphasis when `knowledge_status` time is close to current time
- render propagation source/target more clearly in the information spread panel

Keep the logic presentation-only. Do not add a full social graph system.

**Step 4: Run build**

Run: `cd frontend && npm run build`  
Expected: PASS

**Step 5: Commit**

```bash
git add frontend/components/TownMap.tsx frontend/components/Sidebar.tsx frontend/app/globals.css
git commit -m "feat: strengthen knowledge and relationship cues"
```

---

### Task 4: Add evidence export for report screenshots and structured summary

**Why it matters**

This is the strongest report-writing feature still missing.

The system should be able to export one small evidence package containing:

- current time
- selected phase
- current key events
- current spread chain
- current reflections

This can be exported as JSON or Markdown and then quoted directly in:

- analysis report
- technical solution report
- PPT notes

This avoids hand-copying transient UI state into documents.

**Files:**
- Modify: `backend/app/models.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/simulation.py`
- Create: `scripts/export_demo_evidence.py`
- Modify: `README.md`
- Test: `backend/tests/test_simulation_engine.py`

**Step 1: Write the failing backend test**

```python
from app.simulation import SimulationEngine


def test_export_evidence_contains_phase_and_propagation():
    engine = SimulationEngine()
    for _ in range(12):
        engine.tick()

    evidence = engine.export_evidence()

    assert "time_label" in evidence
    assert "knowledge_status" in evidence
    assert "events" in evidence
    assert "reflections" in evidence
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_simulation_engine.py::test_export_evidence_contains_phase_and_propagation -v`  
Expected: FAIL because export support does not exist.

**Step 3: Write minimal implementation**

Add a backend helper that serializes a compact evidence bundle from current state.

Then add a simple script:

- `scripts/export_demo_evidence.py`

Suggested output targets:

- `submission_docs/evidence/demo_evidence.json`
- `submission_docs/evidence/demo_evidence.md`

The Markdown should be human-readable and directly usable in reports.

**Step 4: Run test and script**

Run:

- `pytest backend/tests/test_simulation_engine.py::test_export_evidence_contains_phase_and_propagation -v`
- `python scripts/export_demo_evidence.py`

Expected:

- test passes
- evidence files are generated

**Step 5: Commit**

```bash
git add backend/app/models.py backend/app/main.py backend/app/simulation.py scripts/export_demo_evidence.py README.md backend/tests/test_simulation_engine.py
git commit -m "feat: add exportable demo evidence bundle"
```

---

### Task 5: Add a paper-vs-demo comparison panel

**Why it matters**

This is a pure explanation feature with very high defense value.

Teachers often ask:

- what part is from the paper
- what part is simplified
- what part is not reproduced

Instead of answering this only verbally, show it on screen in one compact panel:

- paper mechanism
- current demo equivalent
- simplification note

This makes the project feel more rigorous and helps the written report directly.

**Files:**
- Modify: `frontend/app/page.tsx`
- Modify: `frontend/components/Sidebar.tsx`
- Modify: `frontend/app/globals.css`
- Test: `frontend` build via `npm run build`

**Step 1: Write the failing integration check**

Use `npm run build` after introducing the panel props.

**Step 2: Run build to verify it fails**

Run: `cd frontend && npm run build`  
Expected: FAIL until the new panel is fully wired.

**Step 3: Write minimal implementation**

Add a compact static comparison panel, for example:

- `Perception -> current location and nearby agents`
- `Memory stream -> recent memories + memory bank`
- `Retrieval -> retrieved memories with score explanation`
- `Reflection -> reflection panel`
- `Long-term society -> simplified into one deterministic spread chain`

The data can be static frontend content because this is an explanation aid, not simulation logic.

**Step 4: Run build**

Run: `cd frontend && npm run build`  
Expected: PASS

**Step 5: Commit**

```bash
git add frontend/app/page.tsx frontend/components/Sidebar.tsx frontend/app/globals.css
git commit -m "feat: add paper versus demo comparison panel"
```

---

## Recommended Execution Priority

If you only have time for two more features, do:

1. `Scenario bookmarks`
2. `Evidence export`

These two give the best payoff for:

- reducing demo failure risk
- making the report easier to write
- generating reusable evidence

If you have time for three, add:

3. `Mechanism checklist panel`

If you have time for four or five, then add the UI-only explanation aids:

4. `Knowledge / relationship cues`
5. `Paper vs demo comparison panel`

---

## What Not To Add Now

Do **not** spend remaining time on:

- adding more agents
- adding more locations
- rewriting the retrieval algorithm
- making the world more open-ended
- replacing rule retrieval with vector DB
- adding multi-day simulation

Those are expensive and look impressive on paper, but they are worse tradeoffs for a course submission this close to deadline.

---

## Best Report Angle After These Enhancements

If these features are implemented, the report becomes easier to structure around five proof points:

1. deterministic scenario states
2. visible mechanism checklist
3. explicit propagation chain
4. retrieval explanation evidence
5. exportable evidence bundle for screenshots and appendices

That gives you stronger material for:

- “how the system works”
- “what was reproduced from the paper”
- “what was simplified”
- “how the demo proves the mechanism”

---

## Execution Handoff

Plan complete and saved to `docs/plans/2026-06-09-report-video-feature-enrichment-plan.md`. Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?
