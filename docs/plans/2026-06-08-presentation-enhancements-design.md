# Presentation Enhancements Design

## Goal

Improve the current Generative Agents course demo for presentation and review use.

The next iteration should make the system:

- easier to explain during defense and team review
- more stable to operate during live demo and recording
- more explicit about how social spread, memory retrieval, and reflection work

The target is not a larger or smarter simulation. The target is a clearer and more controllable presentation-oriented version of the current demo.

## Product Direction

This design chooses a presentation-first direction:

- explain the existing cognitive loop better
- expose the most important internal state to the UI
- improve demo control and recovery

It does not attempt to expand into:

- larger agent counts
- open-ended sandbox behavior
- scene editing
- full replay infrastructure

That work would increase complexity, but it would not improve defense clarity as much as focused explainability and stability enhancements.

## In Scope

The first enhancement phase includes five features:

1. `Event timeline`
2. `Memory retrieval explanation`
3. `Knowledge spread view`
4. `Speed control`
5. `Demo snapshot save/load`

These five features are selected because they directly improve either:

- presentation clarity
- demo stability

and they fit the current project architecture with limited implementation risk.

## Out of Scope

The following are intentionally excluded from this phase:

- multi-scenario editor
- larger map or larger agent population
- richer perception or visibility simulation
- full replay player with complete historical playback
- major cognition redesign

Those ideas may be useful later, but they are not the best use of effort for the current course-demo objective.

## Why This Scope

The current project already has a workable demo loop:

`plan -> move -> retrieve memories -> act/speak -> spread information -> reflect`

It also already exposes useful UI state:

- current time
- event log
- active plan
- retrieved memories
- recent memories
- reflections
- reasoning note

The gap is not that the system lacks behavior. The gap is that the strongest mechanisms are still only partially visible or only visible through text fragments.

This design makes the hidden structure explicit without requiring a new simulation architecture.

## Feature Design

### 1. Event Timeline

The current `events` list is useful but too close to a generic log. It should be upgraded into a presentation-facing timeline.

The timeline should make it easy to observe:

- when an agent moved
- when a conversation happened
- when gathering knowledge spread
- when reflection was triggered

To support this, timeline events should carry structure in addition to display text:

- `event_type`
- `actor_ids`
- `location_id`
- `tick_count`
- existing human-readable title and detail

This structure allows the frontend to:

- visually group event categories
- highlight important transitions
- make the story progression easy to narrate during defense

### 2. Memory Retrieval Explanation

The project already shows retrieved memories, but it does not clearly show why those memories were selected.

That explanation should become explicit.

For each retrieved memory, the backend should expose:

- total retrieval score
- importance contribution
- recency contribution
- location bonus
- social bonus
- keyword overlap count or equivalent relevance hint

The frontend should display the retrieved memory together with a compact explanation of the dominant reasons it was selected.

This is the most important mechanism-level enhancement in the plan because it makes the agent reasoning loop legible instead of implied.

### 3. Knowledge Spread View

The storyline depends on social propagation, but today that process is only partly visible through dialogue text and `knows_party`.

The system should explicitly track and display:

- who currently knows the gathering
- who told whom
- when each agent first learned about it
- whether the full spread is complete

The frontend should present this as a compact propagation panel. It does not need a complex graph editor. A simple chain or edge list is enough:

- `Alice -> Bob`
- `Bob -> Carol`

This creates a strong and easy-to-explain bridge between local interaction and global social effect.

### 4. Speed Control

The current simulation already has start, pause, tick, and reset. The next step is speed control.

The intended use is presentation control, not open-ended simulation tuning. The system should therefore support a small set of predefined speeds such as:

- `0.5x`
- `1x`
- `2x`

The backend should remain the source of truth for the active speed. The frontend should display the speed returned by the server rather than assuming a local value.

This improves:

- step-by-step explanation
- live demo timing control
- recording repeatability

with minimal architectural cost.

### 5. Demo Snapshot Save/Load

The demo should support saving one stable point and restoring it later.

This is not a full replay system. It is a presentation safety feature.

The snapshot should capture the minimal complete simulation state:

- current time
- tick count
- running flag
- agents
- locations
- events
- story flags
- knowledge-sharing state

Loading a snapshot should restore the world and default to `paused`.

This keeps the user in control and reduces the risk of resuming into an unexpected state during a live demonstration.

## Backend Design

The backend changes should remain incremental.

### Event model

Extend event records with structured metadata while preserving the current readable title/detail fields.

### Retrieval explanation model

Preserve the existing `retrieved_memories` field for compatibility, and add a parallel explanation-oriented structure for the UI.

This avoids forcing every existing consumer to switch to a new format immediately.

### Knowledge spread model

Track propagation explicitly as a small set of edges and first-known timestamps.

The cleanest write point is the successful knowledge-sharing path inside pair interaction handling.

### Speed control API

Add a dedicated endpoint for predefined speed selection. Avoid arbitrary raw values.

### Snapshot API

Add save/load endpoints for a small presentation snapshot system. One snapshot slot is enough for the current goal.

## Frontend Design

The frontend should keep the current single-page structure and enhance it rather than redesigning it.

### Controls

Extend the control panel with:

- speed switching
- snapshot save
- snapshot load

### Timeline panel

Add a dedicated panel for structured story progression. This should feel different from a generic debug log.

### Retrieval explanation panel

Upgrade the current memory display so that it shows both:

- selected memory
- selection reason

### Knowledge spread panel

Add a clear display of gathering awareness and propagation path.

### Snapshot status hint

Show whether a snapshot exists and what world time it represents. This makes the feature safer to use during live demo.

## Data Flow

The data flow remains the same at a high level:

- backend owns authoritative simulation state
- frontend receives periodic state updates over WebSocket
- frontend sends control actions over HTTP

The new features only extend the shape of the world state and the set of control actions.

No local frontend simulation should be introduced.

## Error Handling and Stability Rules

### Speed control

- only accept predefined speed modes
- return the active server-side value after updates
- let the frontend render the confirmed value

### Snapshot loading

- restore all related state together
- default to paused after load
- never partially restore

### WebSocket behavior

- keep the last valid frame on disconnect
- wait for server state confirmation after actions
- do not infer world updates locally

### Retrieval explanation fallback

If explanation details are missing or incomplete, the UI should still show the memory text and render a degraded explanation label instead of failing.

These rules prioritize demo resilience over sophistication.

## Testing Strategy

Testing should focus on the critical demonstration path.

### Backend tests

- timeline events are written with correct structure
- knowledge spread edges are created correctly
- reflection trigger still works after spread completion
- retrieval explanation data is present and consistent
- snapshot save/load restores core state correctly

### API tests

- start
- pause
- tick
- reset
- speed set
- snapshot save
- snapshot load

### Manual demo checks

- reset returns to the fixed opening state
- single tick advances predictably
- `Alice -> Bob -> Carol` is visible in propagation state
- reflection appears after full spread
- snapshot restore brings back time, locations, and event state consistently

## Risks and Mitigations

### Retrieval explanation adds backend complexity

Mitigation:

- keep the current retrieval output
- add explanation output in parallel
- compute explanation from existing score factors rather than introducing a new retrieval algorithm

### Snapshot consistency bugs

Mitigation:

- keep snapshot scope explicit
- restore all related state together
- load into paused mode

### UI clutter

Mitigation:

- keep a single-page layout
- prefer compact panels over new routes
- prioritize presentation value over raw data density

## Recommended Delivery Order

Implement in this order:

1. `Event timeline`
2. `Knowledge spread view`
3. `Speed control`
4. `Memory retrieval explanation`
5. `Demo snapshot save/load`

This order is chosen to maximize visible value early while reducing integration risk for later features.

If time becomes limited, the best stopping point is after the first three features. At that point, the system already becomes significantly better for defense and review.

## Success Criteria

This enhancement phase succeeds if:

- a reviewer can understand the story progression without reading source code
- a presenter can control pacing during demo reliably
- memory retrieval decisions are explainable on-screen
- propagation from Alice to Bob to Carol is explicit
- the demo can recover to a known point quickly if something goes wrong

## Next Step

Use this design as the basis for an implementation plan covering:

- backend model changes
- API additions
- frontend panel updates
- validation and manual demo checklist
