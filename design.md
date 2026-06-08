# Design Document

## Overview

This system is a Smallville-style interactive simulation that reproduces the core loop of generative agents at classroom-demo scale. The design prioritizes clear behavior visibility, low implementation risk, and enough internal mechanism depth to support reports, slides, and an oral demo.

## System Architecture

### Component Map

| Component ID | Name | Type | Responsibility | Interfaces With |
|-------------|------|------|----------------|-----------------|
| COMP-1 | Web UI | Frontend | Render map, panels, logs, dialogue | COMP-2 |
| COMP-2 | Simulation API | Backend | Expose state, control simulation, push updates | COMP-1, COMP-3, COMP-7 |
| COMP-3 | World Engine | Backend Service | Advance time, movement, encounters, events | COMP-4, COMP-5, COMP-6, COMP-7 |
| COMP-4 | Agent Planner | Backend Service | Generate daily plans | COMP-6, COMP-7 |
| COMP-5 | Action Generator | Backend Service | Generate situated actions and dialogue | COMP-6, COMP-7 |
| COMP-6 | Memory System | Backend Service | Store, rank, retrieve, and reflect on memories | COMP-4, COMP-5, COMP-7 |
| COMP-7 | Persistence Layer | Database | Store NPCs, plans, memories, events | COMP-2, COMP-3, COMP-4, COMP-5, COMP-6 |

### High-Level Architecture Diagram

```text
Frontend UI
    |
    v
FastAPI + WebSocket
    |
    v
World Engine ----> Event Log / Persistence
    |                    ^
    |                    |
    +--> Agent Planner --+
    |
    +--> Action Generator <--> LLM Provider
    |
    +--> Memory System -----> SQLite
```

## Data Flow Specifications

### 1. Daily Planning Flow

```text
1. World clock reaches start-of-day
2. World Engine requests plan generation for each NPC
3. Agent Planner builds prompt from profile + prior reflections + current day context
4. LLM returns coarse plan items
5. Plan items are normalized and stored
6. Frontend displays active plan for selected NPC
```

### 2. Situated Action Flow

```text
1. World tick advances
2. World Engine determines current context for an NPC
3. Memory System retrieves relevant memories
4. Action Generator builds prompt from:
   - profile
   - current time
   - current location
   - active plan item
   - nearby agents
   - retrieved memories
5. LLM returns next action and optional utterance
6. World Engine applies movement / wait / talk action
7. Event is written to persistence and UI log
```

### 3. Reflection Flow

```text
1. Memory count threshold or important event threshold is reached
2. Memory System selects recent high-signal memories
3. Reflection prompt is generated
4. LLM returns a concise higher-level summary
5. Reflection memory is stored
6. Future planning and actions can reference it
```

## Integration Points

### Internal Integration Points

| Source | Target | Protocol | Data Format | Purpose |
|--------|--------|----------|-------------|---------|
| Web UI | Simulation API | HTTP / WebSocket | JSON | controls and live updates |
| Simulation API | World Engine | Python call | objects | run simulation logic |
| World Engine | Memory System | Python call | objects | retrieve/store memory |
| Action Generator | LLM Provider | HTTPS | JSON | generate actions and dialogue |
| Agent Planner | LLM Provider | HTTPS | JSON | generate daily plans |
| Reflection Engine | LLM Provider | HTTPS | JSON | produce summaries |

### External Integration Point

#### LLM Provider

**Type:** Online API  
**Purpose:** Generate plan items, situated actions, dialogue, and reflections  
**Authentication:** API key via environment variable  
**Fallback:** Template-based deterministic behavior when API is unavailable for critical demo paths

## Components and Interfaces

### 1. Web UI

**Responsibility:** Present the simulation clearly for demo and explanation.

**Key Views:**

- map view
- selected NPC panel
- timeline/event log
- plan and memory panel

### 2. Simulation API

**Responsibility:** Bridge backend services and frontend observability.

**Candidate endpoints:**

```text
GET  /api/state
POST /api/sim/start
POST /api/sim/pause
POST /api/sim/reset
GET  /api/agents/{id}
WS   /ws/sim
```

### 3. World Engine

**Responsibility:** Own the canonical simulation state.

**Key duties:**

- tick advancement
- time progression
- location occupancy
- encounter detection
- event generation
- state synchronization

### 4. Memory System

**Responsibility:** Maintain agent memory lifecycle.

**Memory ranking heuristic:**

- context relevance
- recency
- importance

Optional later enhancement:

- embedding similarity for the text field

### 5. Agent Planner

**Responsibility:** Create daily coarse schedules for each NPC.

**Output example:**

```json
[
  {"time":"08:00","action":"eat breakfast at home"},
  {"time":"10:00","action":"walk in the park"},
  {"time":"14:00","action":"work at the cafe"}
]
```

### 6. Action Generator

**Responsibility:** Produce the next action from the current situation.

**Expected output schema:**

```json
{
  "action_type": "move|wait|talk",
  "target_location": "cafe",
  "utterance": "Hi Alice, are you still planning the gathering tonight?",
  "reason": "The agent remembers Alice mentioned a gathering earlier."
}
```

## Data Models

### Agent

```python
class Agent:
    id: str
    name: str
    role: str
    personality: str
    home_location: str
    current_location: str
```

### MemoryEntry

```python
class MemoryEntry:
    id: str
    agent_id: str
    type: str
    text: str
    timestamp: str
    location: str
    importance: float
    related_agents: list[str]
```

### PlanItem

```python
class PlanItem:
    id: str
    agent_id: str
    day: str
    time_slot: str
    description: str
```

## Error Handling

### LLM Errors

- retry once for transient failures
- log prompt context identifiers
- fall back to canned behavior where demo continuity matters

### State Errors

- validate action schema before application
- reject impossible moves
- preserve last valid state on parse failure

## Testing Strategy

### Unit Tests

- memory scoring
- plan normalization
- action schema validation
- event creation

### Integration Tests

- simulation tick updates state
- encounter triggers dialogue event
- memory write then retrieval influences action generation

### Demo Validation

- start-to-finish storyline run-through
- API key missing fallback behavior
- WebSocket state updates remain visible in UI

## Deployment

### Local Development

- frontend dev server
- backend dev server
- `.env` for API configuration
- SQLite local file database

### Run Mode

- one-command local startup if possible
- browser-accessible demo for screen recording

## Performance Targets

- visible UI update latency: under 1 second per tick
- initial simulation startup: under 10 seconds locally
- interactive demo with 3 to 5 NPCs on a normal laptop

## Security Considerations

- keep API keys in environment variables only
- do not commit secrets
- sanitize model outputs before state application
