# Generative Agents Demo Design

## Goal

Build a course-demo-scale reproduction of *Generative Agents: Interactive Simulacra of Human Behavior* that is suitable for submission on June 13, 2026.

The target is not a paper-faithful full reproduction. The target is a Smallville-style minimal complete mechanism demo that clearly shows:

- a 2D town scene
- 3 to 5 NPCs with different profiles
- visible movement and time progression
- memory storage and retrieval
- daily planning
- dialogue and social interaction
- lightweight reflection that forms higher-level memories

## Why This Scope

The workspace is currently empty apart from the reference video and assignment template. The delivery deadline is June 13, 2026. A full paper-scale reproduction would create unnecessary schedule risk and would reduce the quality of the demo, report, and presentation.

This design keeps the core paper loop:

`perception -> memory retrieval -> plan -> action/dialogue -> memory update -> reflection`

while intentionally reducing scale, infrastructure complexity, and research ambition.

## In Scope

- One fixed 2D town map with 3 to 4 key locations
- 3 to 5 NPCs with profiles, preferences, and relationships
- World clock and simulation loop
- Daily coarse-grained planning for each NPC
- Situation-aware action generation using an online LLM API
- Memory entries with time, location, related agents, and importance
- Lightweight memory retrieval using relevance, recency, and importance
- Reflection after several important events
- Frontend visualization of:
  - map
  - NPC movement
  - speech bubbles
  - current time
  - selected NPC state
  - recent memories
  - current plan
  - event log
- One designed social storyline for the demo, such as a party invitation spreading through the town

## Out of Scope

- Paper-scale population sizes
- Long-running autonomous society simulation
- Complex vector database infrastructure
- Fine-grained pathfinding research
- Reinforcement learning
- Benchmark replication or quantitative paper-level evaluation
- Multi-modal model input
- Offline local model optimization

## Recommended Stack

- Frontend: React with Next.js
- Backend: Python with FastAPI
- Storage: SQLite plus JSON fields where convenient
- Real-time updates: WebSocket
- Model access: online LLM API with pluggable provider wrapper

This stack minimizes setup cost and maximizes demo velocity.

## Core Architecture

### 1. Frontend Visualization Layer

Displays the town, NPC movement, speech bubbles, timeline, and inspection panels. No autonomous reasoning lives here.

### 2. Simulation Orchestration Layer

Owns the world clock, tick loop, location occupancy, encounter detection, and event dispatching.

### 3. Agent Cognition Layer

Each NPC has:

- profile
- relationships
- daily plan
- recent memories
- reflective memories
- current action state

This layer implements the minimal paper-inspired behavior loop.

### 4. Storage and Model Layer

Persists NPC state, plans, memories, and world events. Wraps LLM calls for planning, action generation, dialogue, and reflection.

## Demo Storyline

The default scripted theme should be socially meaningful rather than random wandering. Recommended storyline:

- Alice plans an evening gathering.
- Alice tells one or two agents during the day.
- The information spreads through encounters.
- Agents update their plans or expectations.
- The final timeline shows relationship and memory effects.

This creates a much stronger classroom demo than isolated movement and random talk.

## Risks and Mitigations

### LLM latency and instability

Mitigation:

- use coarse planning, not per-second generation
- cache repeated prompts where possible
- keep NPC count small
- provide deterministic fallback templates for critical paths

### Frontend/backed integration risk

Mitigation:

- establish a simple event schema early
- make the world loop testable from API output before polishing UI

### Deadline risk

Mitigation:

- build a vertically integrated MVP first
- defer visual polish until the behavior loop is stable
- design reports and slides in parallel with implementation evidence

## Delivery Artifacts Supported by This Design

- source code repository contents
- requirement analysis report material
- technical solution report material
- presentation slides of at least 25 pages
- 20+ minute explanation video mixing theory and practical demo

## Next Step

Use this design as the baseline for:

- `requirements.md`
- `design.md`
- `tasks.md`

and then execute against the phased plan ending on June 13, 2026.
