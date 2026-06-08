# Requirements Document

## Introduction

This project reproduces the core idea of *Generative Agents: Interactive Simulacra of Human Behavior* as a course-demo-scale interactive town simulation. The system targets classroom demonstration rather than paper-level replication, and must deliver visible autonomous behavior backed by a real memory-plan-action loop before June 13, 2026.

## Glossary

- **Agent**: An NPC with profile, memory, plan, and action logic.
- **World Tick**: One simulation update step.
- **Memory Entry**: A stored observation, conversation, or reflection.
- **Reflection**: A higher-level summary distilled from lower-level memories.
- **Plan Item**: A coarse-grained schedule entry for an agent.
- **Encounter**: A situation where two or more agents become co-located and may interact.

## Requirements

### REQ-1 World Simulation

**User Story:** As a reviewer, I want to see a running town simulation, so that the project demonstrates agent behavior in a visible environment.

#### Acceptance Criteria

1. WHEN the demo starts, THE system SHALL render a fixed 2D town map with at least 3 named locations.
2. THE system SHALL simulate at least 3 NPCs moving through the world over time.
3. THE system SHALL display the current in-world time in the UI.
4. THE system SHALL update the visible world state within 1 second of each backend tick.

### REQ-2 Agent Identity

**User Story:** As a reviewer, I want each NPC to exhibit distinct behavior, so that the simulation does not look scripted in a uniform way.

#### Acceptance Criteria

1. THE system SHALL define a profile for each NPC including name, role, personality summary, and preferences.
2. WHEN two NPCs are observed across multiple events, THE system SHALL preserve their identities consistently.
3. THE system SHALL expose the selected NPC's profile in the UI.

### REQ-3 Planning

**User Story:** As a reviewer, I want NPCs to follow daily plans, so that their actions appear purposeful rather than random.

#### Acceptance Criteria

1. WHEN a new simulation day begins, THE system SHALL generate a coarse-grained plan for each NPC.
2. THE system SHALL store each NPC's current plan items and active plan step.
3. WHEN the current time reaches a planned period, THE system SHALL use that plan as context for action generation.

### REQ-4 Memory

**User Story:** As a reviewer, I want agents to remember prior events, so that later behavior can depend on prior interactions.

#### Acceptance Criteria

1. WHEN an agent observes an event or conversation, THE system SHALL create a memory entry containing text, timestamp, and location.
2. THE system SHALL assign an importance score to each memory entry.
3. WHEN generating a new action, THE system SHALL retrieve relevant memories using recency, importance, and context relevance.
4. THE system SHALL display recent memories for the selected NPC.

### REQ-5 Social Interaction

**User Story:** As a reviewer, I want agents to converse and influence one another, so that the simulation resembles a social environment.

#### Acceptance Criteria

1. WHEN agents meet at the same location, THE system SHALL be able to trigger a dialogue event.
2. THE system SHALL show dialogue or speech bubbles in the frontend.
3. WHEN one agent communicates new information to another, THE recipient SHALL record a corresponding memory.
4. THE system SHALL support at least one information-spreading storyline across multiple NPCs.

### REQ-6 Reflection

**User Story:** As a reviewer, I want to see higher-level memory formation, so that the project reflects a key paper mechanism.

#### Acceptance Criteria

1. WHEN an agent accumulates enough recent events or an important event occurs, THE system SHALL generate a reflection memory.
2. THE system SHALL persist reflection memories separately from raw observations.
3. THE system SHALL display reflective summaries for the selected NPC.

### REQ-7 Demo Observability

**User Story:** As a presenter, I want the system state to be observable, so that I can explain the mechanism during the recorded presentation.

#### Acceptance Criteria

1. THE UI SHALL include an event log of recent actions and interactions.
2. THE UI SHALL show the selected NPC's current action.
3. THE UI SHALL show the selected NPC's current plan and recent memories.
4. THE system SHALL keep enough logs to support screenshots and report writing.

### REQ-8 Deliverability

**User Story:** As a course team, I want the project outputs to match the assignment format, so that the final submission is complete.

#### Acceptance Criteria

1. THE project SHALL include runnable source code and configuration instructions.
2. THE project SHALL produce enough architectural and experimental material to support a technical solution report.
3. THE project SHALL produce enough background, scope, and rationale material to support a requirement analysis report.
4. THE project SHALL support a presentation of at least 25 slides and a 20+ minute demo video by June 13, 2026.
