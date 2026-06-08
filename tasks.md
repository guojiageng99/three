# Implementation Plan

- [ ] 1. Project Setup
  - Create frontend and backend project skeletons.
  - Define shared JSON schemas for agents, plans, memories, and events.
  - Add environment variable handling and local configuration.
  - _Requirements: REQ-8_

- [ ] 2. Core Simulation Infrastructure
  - Implement world clock and simulation tick loop.
  - Define map locations and adjacency or travel rules.
  - Implement NPC location updates and occupancy tracking.
  - _Requirements: REQ-1, REQ-7_

- [ ] 3. Agent Profiles and Initial World State
  - Create 3 to 5 NPC profiles with distinct roles and personalities.
  - Define initial relationships and location assignments.
  - Prepare a demo storyline seed centered on one social event.
  - _Requirements: REQ-2, REQ-5_

- [ ] 4. Planning System
  - Implement daily plan prompt generation.
  - Parse and normalize plan outputs into stored plan items.
  - Link active plan items to current simulation time.
  - _Requirements: REQ-3_
  - _Dependencies: Task 1, Task 3_

- [ ] 5. Memory System
  - Implement memory persistence schema.
  - Record observation and conversation memories.
  - Implement ranking by recency, importance, and relevance.
  - Expose recent and retrieved memories to the agent pipeline.
  - _Requirements: REQ-4_
  - _Dependencies: Task 1, Task 3_

- [ ] 6. Action and Dialogue Generation
  - Build prompts using profile, plan, context, and memories.
  - Implement safe parsing of action outputs.
  - Support move, wait, and talk action types.
  - Log all generated actions for debugging and reporting.
  - _Requirements: REQ-3, REQ-5, REQ-7_
  - _Dependencies: Task 4, Task 5_

- [ ] 7. Reflection Mechanism
  - Define reflection trigger thresholds.
  - Summarize recent memories into higher-level reflections.
  - Store and display reflection memories.
  - Feed reflections back into future planning prompts.
  - _Requirements: REQ-6_
  - _Dependencies: Task 5, Task 6_

- [ ] 8. Backend API and Real-Time Updates
  - Expose state inspection endpoints.
  - Implement start, pause, and reset controls.
  - Push simulation updates through WebSocket.
  - _Requirements: REQ-1, REQ-7, REQ-8_
  - _Dependencies: Task 2, Task 4, Task 5, Task 6_

- [ ] 9. Frontend Demo Interface
  - Build 2D town map view.
  - Render NPC positions and movement.
  - Show speech bubbles during dialogue.
  - Add side panels for plan, memory, reflection, and current action.
  - Add event log and selected NPC inspection.
  - _Requirements: REQ-1, REQ-2, REQ-4, REQ-5, REQ-6, REQ-7_
  - _Dependencies: Task 8_

- [ ] 10. Storyline and Demo Stabilization
  - Tune the social storyline to ensure visible information spread.
  - Add fallback deterministic behavior for critical demo continuity.
  - Validate one full recorded demonstration path end to end.
  - _Requirements: REQ-5, REQ-6, REQ-7, REQ-8_
  - _Dependencies: Task 6, Task 7, Task 9_

- [ ] 11. Documentation and Submission Material Support
  - Write README with setup and run instructions.
  - Capture architecture screenshots and logs for reports.
  - Organize evidence for the requirement analysis report and technical solution report.
  - _Requirements: REQ-8_
  - _Dependencies: Task 10_

- [ ] 12. Deadline-Oriented Delivery Schedule
  - June 4, 2026: project skeleton, architecture, data schema
  - June 5, 2026: map UI and world loop
  - June 6, 2026: profiles and planning
  - June 7, 2026: memory system
  - June 8, 2026: action and dialogue generation
  - June 9, 2026: reflection and storyline
  - June 10, 2026: stabilization and README
  - June 11, 2026: requirement analysis report and technical solution report
  - June 12, 2026: slide deck and rehearsal recording
  - June 13, 2026: final recording and packaging
  - _Requirements: REQ-8_
