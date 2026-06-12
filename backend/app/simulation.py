from __future__ import annotations

import json
import os
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

from .cognition import ActionDecision, AgentCognition, DialogueDecision
from .models import Agent, DemoBookmark, EventLog, KnowledgeEdge, Location, MemoryEntry, PlanItem, SnapshotStatus, WorldState


class SimulationEngine:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        configured_mode = os.getenv("SIMULATION_MODE", "deterministic").strip().lower()
        self.simulation_mode = configured_mode if configured_mode in {"deterministic", "llm"} else "deterministic"
        self.reflection_importance_threshold = self._float_env("REFLECTION_IMPORTANCE_THRESHOLD", 2.4)
        self._speed_presets = {
            "0.5x": 4.0,
            "1x": 2.0,
            "2x": 1.0,
        }
        self._active_speed_label = "1x"
        self._tick_interval_seconds = self._speed_presets[self._active_speed_label]
        self._snapshot_bundle: dict | None = None
        self._bookmarks = self._build_bookmarks()
        self._cognition = AgentCognition(self.simulation_mode)
        self._jumping = False
        self.reset()

    def reset(self) -> None:
        with self._lock:
            self.running = False
            self.current_time = datetime(2026, 6, 4, 8, 0)
            self.tick_count = 0
            self.locations = self._build_locations()
            self.agents = self._build_agents()
            self.events: list[EventLog] = []
            self.knowledge_edges: list[KnowledgeEdge] = []
            self.knowledge_status: dict[str, str] = {"alice": "08:00"}
            self.story_flags = {
                "party_reflection_written": False,
                "party_shared_tick_count": None,
            }
            self.reflection_trigger_reason: str | None = None
            self.shared_pairs: set[tuple[str, str]] = set()
            self._refresh_recent_memories()
            day_label = self.current_time.strftime("%Y-%m-%d")
            time_label = self.current_time.strftime("%H:%M")
            agents_snapshot = deepcopy(self.agents)
            locations_snapshot = deepcopy(self.locations)

        plan_updates = self._generate_plans_outside_lock(agents_snapshot, locations_snapshot, day_label)

        with self._lock:
            for agent in self.agents:
                if agent.id in plan_updates:
                    agent.plan = plan_updates[agent.id]
                agent.active_plan = self._active_plan_item(agent, time_label)
            self._seed_opening_event()

    def start(self) -> None:
        with self._lock:
            if self.running:
                return
            self.running = True

        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()

    def pause(self) -> None:
        with self._lock:
            self.running = False

    def shutdown(self) -> None:
        self._stop_event.set()
        with self._lock:
            self.running = False

    def set_speed(self, speed_label: str) -> str:
        with self._lock:
            if speed_label not in self._speed_presets:
                raise ValueError(f"Unsupported speed label: {speed_label}")
            self._active_speed_label = speed_label
            self._tick_interval_seconds = self._speed_presets[speed_label]
            return self._active_speed_label

    def save_snapshot(self) -> SnapshotStatus:
        with self._lock:
            self._snapshot_bundle = {
                "current_time": self.current_time,
                "tick_count": self.tick_count,
                "locations": deepcopy(self.locations),
                "agents": deepcopy(self.agents),
                "events": deepcopy(self.events),
                "knowledge_edges": deepcopy(self.knowledge_edges),
                "knowledge_status": deepcopy(self.knowledge_status),
                "story_flags": deepcopy(self.story_flags),
                "reflection_trigger_reason": self.reflection_trigger_reason,
                "shared_pairs": deepcopy(self.shared_pairs),
                "active_speed_label": self._active_speed_label,
            }
            return self._snapshot_status()

    def load_snapshot(self) -> SnapshotStatus:
        with self._lock:
            if not self._snapshot_bundle:
                raise ValueError("No snapshot saved")
            bundle = deepcopy(self._snapshot_bundle)
            self.current_time = bundle["current_time"]
            self.tick_count = bundle["tick_count"]
            self.running = False
            self.locations = bundle["locations"]
            self.agents = bundle["agents"]
            self.events = bundle["events"]
            self.knowledge_edges = bundle["knowledge_edges"]
            self.knowledge_status = bundle["knowledge_status"]
            self.story_flags = bundle["story_flags"]
            self.reflection_trigger_reason = bundle.get("reflection_trigger_reason")
            self.shared_pairs = bundle["shared_pairs"]
            self._active_speed_label = bundle["active_speed_label"]
            self._tick_interval_seconds = self._speed_presets[self._active_speed_label]
            return self._snapshot_status()

    def jump_to_bookmark(self, bookmark_key: str) -> DemoBookmark:
        bookmark = next((item for item in self._bookmarks if item.key == bookmark_key), None)
        if bookmark is None:
            raise ValueError(f"Unsupported bookmark: {bookmark_key}")

        self._jumping = True
        try:
            current = self.current_time.strftime("%H:%M")
            if current >= bookmark.target_time:
                self.reset()
            while self.current_time.strftime("%H:%M") < bookmark.target_time:
                self.tick()
                time.sleep(0.5)
        finally:
            self._jumping = False

        with self._lock:
            self.running = False
            self._prune_events_for_bookmark(bookmark.target_time)
        return bookmark

    def export_evidence(self) -> dict:
        snapshot = self.snapshot()
        reflections = {
            agent.name: [memory.text for memory in agent.reflections]
            for agent in snapshot.agents
            if agent.reflections
        }
        return {
            "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "day_label": snapshot.day_label,
            "time_label": snapshot.time_label,
            "tick_count": snapshot.tick_count,
            "phase_label": self._phase_label(snapshot),
            "simulation_mode": snapshot.simulation_mode,
            "llm_provider": snapshot.llm_provider,
            "llm_model": snapshot.llm_model,
            "llm_status": snapshot.last_llm_call_status,
            "memory_stream_count": snapshot.memory_stream_count,
            "reflection_trigger_reason": snapshot.reflection_trigger_reason,
            "knowledge_status": snapshot.knowledge_status,
            "knowledge_edges": [edge.model_dump() for edge in snapshot.knowledge_edges],
            "events": [event.model_dump() for event in snapshot.events[:8]],
            "reflections": reflections,
            "selected_proof_points": [
                "Plan-driven movement is visible on the town map.",
                "Dialogue spread is recorded in the event timeline and propagation chain.",
                "Retrieved memories explain why an agent acts in the current context.",
                "Reflection appears after social knowledge spreads and memory importance crosses the threshold.",
                "In LLM mode, each character is prompted as an independent agent with its own profile and private memories.",
            ],
        }

    def export_evidence_files(self, output_dir: Path) -> tuple[Path, Path]:
        evidence = self.export_evidence()
        output_dir.mkdir(parents=True, exist_ok=True)

        json_path = output_dir / "demo_evidence.json"
        md_path = output_dir / "demo_evidence.md"

        json_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
        md_path.write_text(self._build_evidence_markdown(evidence), encoding="utf-8")

        return json_path, md_path

    def tick(self) -> None:
        pending_actions: list[dict] = []
        pending_interactions: list[dict] = []

        with self._lock:
            self.current_time += timedelta(minutes=30)
            self.tick_count += 1
            time_label = self.current_time.strftime("%H:%M")

            for agent in self.agents:
                active_item = self._active_plan_item(agent, time_label)
                agent.active_plan = active_item
                if active_item.location_id != agent.current_location_id:
                    previous = agent.current_location_id
                    agent.current_location_id = active_item.location_id
                    agent.current_action = f"Heading to {self._location_name(active_item.location_id)}"
                    self._add_event(
                        f"{agent.name} moved",
                        f"{agent.name} left {self._location_name(previous)} and went to {self._location_name(active_item.location_id)}.",
                        event_type="move",
                        actor_ids=[agent.id],
                        location_id=active_item.location_id,
                    )
                    self._remember(
                        agent,
                        "observation",
                        f"I moved to {self._location_name(active_item.location_id)} for {active_item.summary}.",
                        active_item.location_id,
                        0.35,
                    )
                nearby_agents = [
                    other
                    for other in self.agents
                    if other.id != agent.id and other.current_location_id == agent.current_location_id
                ]
                retrieved, retrieval_explanations = self._cognition.retrieve_memories_with_explanations(
                    agent=agent,
                    active_plan=active_item,
                    current_location=self._location(agent.current_location_id),
                    nearby_agents=nearby_agents,
                    time_label=time_label,
                )
                pending_actions.append(
                    {
                        "agent_id": agent.id,
                        "agent": deepcopy(agent),
                        "active_plan": deepcopy(active_item),
                        "location": deepcopy(self._location(agent.current_location_id)),
                        "nearby_agents": deepcopy(nearby_agents),
                        "retrieved_memories": deepcopy(retrieved),
                        "retrieval_explanations": deepcopy(retrieval_explanations),
                        "time_label": time_label,
                    }
                )

            pending_interactions = self._collect_pending_interactions(time_label)

        def _generate_action(item: dict) -> dict:
            return {
                **item,
                "decision": self._cognition.generate_action(
                    agent=item["agent"],
                    active_plan=item["active_plan"],
                    current_location=item["location"],
                    nearby_agents=item["nearby_agents"],
                    retrieved_memories=item["retrieved_memories"],
                    time_label=item["time_label"],
                ),
            }

        with ThreadPoolExecutor(max_workers=4) as pool:
            action_results = list(pool.map(_generate_action, pending_actions))
            interaction_results = list(pool.map(self._generate_dialogue_outside_lock, pending_interactions))

        reflection_payload: tuple[str | None, list[dict]] | None = None
        with self._lock:
            for item in action_results:
                self._apply_action_result(item)

            for item in interaction_results:
                self._apply_dialogue_result(item)

            if self._party_knowers_count() >= 3 and self.story_flags["party_shared_tick_count"] is None:
                self.story_flags["party_shared_tick_count"] = self.tick_count

            reflection_payload = self._prepare_reflection_payload(time_label)

        reflection_results: list[dict] = []
        reflection_reason: str | None = None
        if reflection_payload is not None:
            reflection_reason, reflection_agents = reflection_payload
            reflection_results = [
                {
                    "agent_id": item["agent_id"],
                    "text": self._cognition.generate_reflection(item["agent"], time_label),
                }
                for item in reflection_agents
            ]

        with self._lock:
            if reflection_results and reflection_reason:
                self.reflection_trigger_reason = reflection_reason
                self._apply_reflection_results(reflection_results, time_label)
            self._trim_logs()

    def snapshot(self) -> WorldState:
        with self._lock:
            return WorldState(
                day_label=self.current_time.strftime("%Y-%m-%d"),
                time_label=self.current_time.strftime("%H:%M"),
                running=self.running,
                tick_count=self.tick_count,
                simulation_mode=self.simulation_mode,
                llm_enabled=self._cognition.enabled,
                llm_provider=self._cognition.provider if self._cognition.enabled else None,
                llm_model=self._cognition.model if self._cognition.enabled else None,
                last_llm_call_status=self._cognition.last_llm_call_status,
                reflection_trigger_reason=self.reflection_trigger_reason,
                memory_stream_count=self._memory_stream_count(),
                locations=deepcopy(self.locations),
                agents=deepcopy(self.agents),
                events=deepcopy(list(reversed(self.events[-12:]))),
                knowledge_edges=deepcopy(self.knowledge_edges),
                knowledge_status=deepcopy(self.knowledge_status),
                active_speed_label=self._active_speed_label,
                available_speed_labels=list(self._speed_presets.keys()),
                available_bookmarks=deepcopy(self._bookmarks),
                snapshot_status=self._snapshot_status(),
            )

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            with self._lock:
                should_tick = self.running
                interval = self._tick_interval_seconds
            if should_tick:
                self.tick()
            time.sleep(interval)

    def _build_locations(self) -> list[Location]:
        return [
            Location(id="home_alice", name="Alice's Home", x=8, y=18, description="A warm apartment with party notes on the table."),
            Location(id="park", name="Johnson Park", x=42, y=10, description="A calm open park for walking and chance encounters."),
            Location(id="cafe", name="Hobbs Cafe", x=72, y=22, description="A small cafe where agents work and chat."),
            Location(id="square", name="Town Square", x=48, y=46, description="The social center of the town."),
        ]

    def _build_bookmarks(self) -> list[DemoBookmark]:
        return [
            DemoBookmark(
                key="initial",
                label="08:00 初始态",
                target_time="08:00",
                description="只有 Alice 知道聚会，最适合讲初始计划与人物设定。",
            ),
            DemoBookmark(
                key="first_spread",
                label="10:00 第一次传播",
                target_time="10:00",
                description="Alice 在咖啡馆告诉 Bob，最适合讲对话如何改变角色状态。",
            ),
            DemoBookmark(
                key="second_spread",
                label="14:00 第二次传播",
                target_time="14:00",
                description="Bob 在广场告诉 Carol，最适合讲局部互动如何累积成全局传播。",
            ),
            DemoBookmark(
                key="reflection",
                label="14:30 反思形成态",
                target_time="14:30",
                description="三人都知道信息后形成 reflection，最适合讲高层总结。",
            ),
        ]

    def _build_agents(self) -> list[Agent]:
        alice_plan = [
            PlanItem(time_slot="08:00", location_id="home_alice", summary="Preparing notes for tonight's gathering"),
            PlanItem(time_slot="10:00", location_id="cafe", summary="Working at the cafe and inviting a friend"),
            PlanItem(time_slot="14:00", location_id="square", summary="Buying small decorations"),
            PlanItem(time_slot="18:00", location_id="home_alice", summary="Getting ready to host the gathering"),
        ]
        bob_plan = [
            PlanItem(time_slot="08:00", location_id="park", summary="Taking a morning walk"),
            PlanItem(time_slot="10:00", location_id="cafe", summary="Writing in the cafe"),
            PlanItem(time_slot="14:00", location_id="square", summary="Meeting people in the square"),
            PlanItem(time_slot="18:00", location_id="park", summary="Taking an evening walk"),
        ]
        carol_plan = [
            PlanItem(time_slot="08:00", location_id="square", summary="Opening the flower stall"),
            PlanItem(time_slot="10:00", location_id="park", summary="Delivering flowers near the park"),
            PlanItem(time_slot="14:00", location_id="square", summary="Selling flowers and chatting with neighbors"),
            PlanItem(time_slot="18:00", location_id="square", summary="Closing the stall and checking town news"),
        ]
        return [
            Agent(
                id="alice",
                name="Alice",
                role="Researcher",
                personality="Thoughtful, proactive, and social when she has a purpose.",
                color="#ff7f50",
                current_location_id="home_alice",
                current_action="Preparing notes for tonight's gathering",
                knows_party=True,
                profile_summary="Alice is planning a small evening gathering and wants to invite a few friends naturally during the day.",
                plan=alice_plan,
                active_plan=alice_plan[0],
                memory_bank=[
                    self._memory("observation", "I want tonight's gathering to feel casual and welcoming.", "08:00", "home_alice", 0.82),
                ],
            ),
            Agent(
                id="bob",
                name="Bob",
                role="Journalist",
                personality="Curious, observant, and quick to spread interesting local news.",
                color="#5ab1ef",
                current_location_id="park",
                current_action="Taking a morning walk",
                profile_summary="Bob likes learning what is happening around town and often passes news between people.",
                plan=bob_plan,
                active_plan=bob_plan[0],
                memory_bank=[
                    self._memory("observation", "I should spend some time writing at the cafe today.", "08:00", "park", 0.4),
                ],
            ),
            Agent(
                id="carol",
                name="Carol",
                role="Florist",
                personality="Warm, practical, and attentive to the town's social rhythm.",
                color="#7cd992",
                current_location_id="square",
                current_action="Opening the flower stall",
                profile_summary="Carol notices community events quickly and often reacts by helping in practical ways.",
                plan=carol_plan,
                active_plan=carol_plan[0],
                memory_bank=[
                    self._memory("observation", "The square is busiest in the afternoon.", "08:00", "square", 0.36),
                ],
            ),
        ]

    def _seed_opening_event(self) -> None:
        self._add_event(
            "Simulation ready",
            "The town wakes up. Alice has an evening gathering in mind, but only she knows about it yet.",
            event_type="system",
            actor_ids=["alice"],
            location_id="home_alice",
        )

    def _agent_by_id(self, agent_id: str) -> Agent:
        return next(agent for agent in self.agents if agent.id == agent_id)

    def _generate_plans_outside_lock(
        self,
        agents: list[Agent],
        locations: list[Location],
        day_label: str,
    ) -> dict[str, list[PlanItem]]:
        plan_updates: dict[str, list[PlanItem]] = {}
        for agent in agents:
            generated = self._cognition.generate_plan(agent, locations, day_label)
            if generated:
                plan_updates[agent.id] = generated
        return plan_updates

    def _apply_action_result(self, item: dict) -> None:
        agent = self._agent_by_id(item["agent_id"])
        decision: ActionDecision = item["decision"]
        nearby_agents = [
            other
            for other in self.agents
            if other.id != agent.id and other.current_location_id == agent.current_location_id
        ]
        agent.retrieved_memories = item["retrieved_memories"]
        agent.retrieval_explanations = item["retrieval_explanations"]
        agent.current_action = decision.summary
        agent.last_utterance = decision.utterance
        agent.reasoning_note = decision.reasoning_note
        self._remember(
            agent,
            "action",
            f"I chose this action: {decision.summary}.",
            agent.current_location_id,
            0.22,
            [other.id for other in nearby_agents],
        )

    def _collect_pending_interactions(self, time_label: str) -> list[dict]:
        encounters: dict[str, list[Agent]] = defaultdict(list)
        for agent in self.agents:
            encounters[agent.current_location_id].append(agent)

        pending: list[dict] = []
        for location_id, occupants in encounters.items():
            if len(occupants) < 2:
                continue
            knowers = [agent for agent in occupants if agent.knows_party]
            listeners = [agent for agent in occupants if not agent.knows_party]
            if not listeners or not knowers:
                continue
            location = self._location(location_id)
            for listener in listeners:
                preferred_speaker = next((agent for agent in knowers if agent.id != "alice"), knowers[0])
                speaker, other = (preferred_speaker, listener)
                if not speaker.knows_party:
                    speaker, other = other, speaker
                pair_key = tuple(sorted([speaker.id, other.id]))
                if pair_key in self.shared_pairs:
                    continue
                pending.append(
                    {
                        "speaker_id": speaker.id,
                        "listener_id": other.id,
                        "speaker": deepcopy(speaker),
                        "listener": deepcopy(other),
                        "location": deepcopy(location),
                        "time_label": time_label,
                        "pair_key": pair_key,
                    }
                )
        return pending

    def _generate_dialogue_outside_lock(self, item: dict) -> dict:
        speaker_retrieved, speaker_explanations = self._cognition.retrieve_memories_with_explanations(
            agent=item["speaker"],
            active_plan=self._active_plan_item(item["speaker"], item["time_label"]),
            current_location=item["location"],
            nearby_agents=[item["listener"]],
            time_label=item["time_label"],
        )
        decision = self._cognition.generate_dialogue(
            speaker=item["speaker"],
            listener=item["listener"],
            current_location=item["location"],
            retrieved_memories=speaker_retrieved,
            time_label=item["time_label"],
        )
        listener_retrieved, listener_explanations = self._cognition.retrieve_memories_with_explanations(
            agent=item["listener"],
            active_plan=self._active_plan_item(item["listener"], item["time_label"]),
            current_location=item["location"],
            nearby_agents=[item["speaker"]],
            time_label=item["time_label"],
        )
        return {
            **item,
            "decision": decision,
            "speaker_retrieved": speaker_retrieved,
            "speaker_explanations": speaker_explanations,
            "listener_retrieved": listener_retrieved,
            "listener_explanations": listener_explanations,
        }

    def _apply_dialogue_result(self, item: dict) -> None:
        if item["pair_key"] in self.shared_pairs:
            return

        speaker = self._agent_by_id(item["speaker_id"])
        listener = self._agent_by_id(item["listener_id"])
        if speaker.knows_party == listener.knows_party:
            return

        decision: DialogueDecision = item["decision"]
        self.shared_pairs.add(item["pair_key"])
        listener_learned_now = decision.listener_learns_party and listener.id not in self.knowledge_status
        listener.knows_party = decision.listener_learns_party or listener.knows_party
        if listener_learned_now:
            self.knowledge_status[listener.id] = item["time_label"]
            self.knowledge_edges.append(
                KnowledgeEdge(
                    source_agent_id=speaker.id,
                    target_agent_id=listener.id,
                    learned_at=item["time_label"],
                    tick_count=self.tick_count,
                )
            )
        speaker.current_action = "Sharing a socially relevant update"
        listener.current_action = "Reacting to new social information"
        speaker.last_utterance = decision.speaker_utterance
        listener.last_utterance = decision.listener_utterance
        speaker.reasoning_note = (
            f"{speaker.name} knows the gathering and sees {listener.name} nearby, so the social information is shared."
        )
        listener.reasoning_note = (
            f"{listener.name} received new social information from {speaker.name} during the encounter."
        )
        self._add_event(
            decision.event_title,
            decision.event_detail,
            event_type="share" if decision.listener_learns_party else "conversation",
            actor_ids=[speaker.id, listener.id],
            location_id=item["location"].id,
        )
        self._remember(speaker, "conversation", decision.speaker_memory, item["location"].id, 0.84, [listener.id])
        self._remember(listener, "conversation", decision.listener_memory, item["location"].id, 0.88, [speaker.id])
        speaker.retrieved_memories = item["speaker_retrieved"]
        speaker.retrieval_explanations = item["speaker_explanations"]
        listener.retrieved_memories = item["listener_retrieved"]
        listener.retrieval_explanations = item["listener_explanations"]

    def _prepare_reflection_payload(self, time_label: str) -> tuple[str | None, list[dict]] | None:
        if self.story_flags["party_reflection_written"]:
            return None
        if self._party_knowers_count() < 3:
            return None
        shared_tick_count = self.story_flags.get("party_shared_tick_count")
        if shared_tick_count is None or self.tick_count <= shared_tick_count:
            return None

        eligible_agents = [agent for agent in self.agents if agent.knows_party]
        importance_scores = {
            agent.id: self._reflection_importance_score(agent)
            for agent in eligible_agents
        }
        if not eligible_agents or any(score < self.reflection_importance_threshold for score in importance_scores.values()):
            return None

        reflection_reason = (
            f"Shared knowledge reached all agents and memory importance crossed "
            f"{self.reflection_importance_threshold:.2f}: "
            + ", ".join(f"{agent_id}={score:.2f}" for agent_id, score in importance_scores.items())
        )
        reflection_agents = [
            {"agent_id": agent.id, "agent": deepcopy(agent)}
            for agent in self.agents
            if agent.knows_party
        ]
        return reflection_reason, reflection_agents

    def _apply_reflection_results(self, reflection_results: list[dict], time_label: str) -> None:
        self.story_flags["party_reflection_written"] = True
        reflection_actors: list[str] = []
        for item in reflection_results:
            agent = self._agent_by_id(item["agent_id"])
            reflection_actors.append(agent.id)
            reflection = self._memory(
                "reflection",
                item["text"],
                self.current_time.strftime("%H:%M"),
                agent.current_location_id,
                0.93,
                ["alice", "bob", "carol"],
            )
            agent.reflections.insert(0, reflection)
            agent.reflections = agent.reflections[:3]
            agent.memory_bank.insert(0, reflection)
            agent.recent_memories = agent.memory_bank[:5]
            agent.current_action = "Reflecting on how the gathering has become shared town knowledge"
            agent.reasoning_note = self.reflection_trigger_reason or (
                "A new high-level reflection was formed because the social information spread across the town."
            )
        self._add_event(
            "Reflection formed",
            "The agents now treat Alice's gathering as a shared town event after memory importance crossed the reflection threshold.",
            event_type="reflection",
            actor_ids=reflection_actors,
        )

    def _memory(
        self,
        memory_type: str,
        text: str,
        timestamp: str,
        location_id: str,
        importance: float,
        related_agents: list[str] | None = None,
    ) -> MemoryEntry:
        return MemoryEntry(
            id=uuid4().hex,
            type=memory_type,
            text=text,
            timestamp=timestamp,
            location_id=location_id,
            importance=importance,
            related_agents=related_agents or [],
        )

    def _remember(
        self,
        agent: Agent,
        memory_type: str,
        text: str,
        location_id: str,
        importance: float,
        related_agents: list[str] | None = None,
    ) -> None:
        entry = self._memory(
            memory_type,
            text,
            self.current_time.strftime("%H:%M"),
            location_id,
            importance,
            related_agents,
        )
        agent.memory_bank.insert(0, entry)
        agent.recent_memories = agent.memory_bank[:5]

    def _active_plan_item(self, agent: Agent, time_label: str) -> PlanItem:
        active = agent.plan[0]
        for item in agent.plan:
            if item.time_slot <= time_label:
                active = item
        return active

    def _location_name(self, location_id: str) -> str:
        return next(location.name for location in self.locations if location.id == location_id)

    def _location(self, location_id: str) -> Location:
        return next(location for location in self.locations if location.id == location_id)

    def _party_knowers_count(self) -> int:
        return sum(1 for agent in self.agents if agent.knows_party)

    def _reflection_importance_score(self, agent: Agent) -> float:
        return sum(memory.importance for memory in agent.memory_bank if memory.type != "reflection")

    def _memory_stream_count(self) -> int:
        return sum(len(agent.memory_bank) for agent in self.agents)

    def _refresh_recent_memories(self) -> None:
        for agent in self.agents:
            agent.recent_memories = agent.memory_bank[:5]

    def _add_event(
        self,
        title: str,
        detail: str,
        event_type: str = "system",
        actor_ids: list[str] | None = None,
        location_id: str | None = None,
    ) -> None:
        self.events.append(
            EventLog(
                id=uuid4().hex,
                time=self.current_time.strftime("%H:%M"),
                title=title,
                detail=detail,
                event_type=event_type,
                actor_ids=actor_ids or [],
                location_id=location_id,
                tick_count=self.tick_count,
            )
        )

    def _trim_logs(self) -> None:
        self.events = self.events[-30:]

    def _prune_events_for_bookmark(self, target_time: str) -> None:
        """书签跳转后，移除中间移动事件，只保留叙事关键事件。"""
        self.events = [
            event for event in self.events
            if event.event_type != "move"
            or event.time == target_time
        ]

    def _snapshot_status(self) -> SnapshotStatus:
        if not self._snapshot_bundle:
            return SnapshotStatus(exists=False)
        return SnapshotStatus(
            exists=True,
            label=self._snapshot_bundle["current_time"].strftime("%Y-%m-%d %H:%M"),
            tick_count=self._snapshot_bundle["tick_count"],
        )

    def _phase_label(self, snapshot: WorldState) -> str:
        if any(agent.reflections for agent in snapshot.agents):
            return "反思形成"
        if len(snapshot.knowledge_status) >= 3:
            return "传播完成"
        if len(snapshot.knowledge_status) >= 2:
            return "开始传播"
        return "初始准备"

    def _build_evidence_markdown(self, evidence: dict) -> str:
        knowledge_lines = "\n".join(
            f"- `{agent_id}` 在 `{learned_at}` 获得聚会信息" for agent_id, learned_at in evidence["knowledge_status"].items()
        )
        edge_lines = "\n".join(
            f"- `{edge['source_agent_id']}` -> `{edge['target_agent_id']}` at `{edge['learned_at']}`"
            for edge in evidence["knowledge_edges"]
        )
        event_lines = "\n".join(
            f"- `{event['time']}` [{event['event_type']}] {event['title']}: {event['detail']}" for event in evidence["events"]
        )
        reflection_lines = "\n".join(
            f"- **{agent_name}**: {'; '.join(texts)}" for agent_name, texts in evidence["reflections"].items()
        )
        proof_lines = "\n".join(f"- {line}" for line in evidence["selected_proof_points"])

        return f"""# Demo Evidence Export

## Snapshot

- 导出时间：`{evidence['exported_at']}`
- 仿真日期：`{evidence['day_label']}`
- 当前时间：`{evidence['time_label']}`
- Tick：`{evidence['tick_count']}`
- 当前阶段：`{evidence['phase_label']}`
- 仿真模式：`{evidence['simulation_mode']}`
- LLM 供应商：`{evidence.get('llm_provider') or '未启用'}`
- LLM 模型：`{evidence.get('llm_model') or '未启用'}`
- LLM 状态：`{evidence['llm_status']}`
- 记忆流条数：`{evidence['memory_stream_count']}`
- 反思触发原因：`{evidence['reflection_trigger_reason'] or '尚未触发'}`

## Knowledge Status

{knowledge_lines or '- 暂无传播记录'}

## Propagation Chain

{edge_lines or '- 暂无传播链'}

## Key Events

{event_lines or '- 暂无关键事件'}

## Reflections

{reflection_lines or '- 暂无反思生成'}

## Proof Points

{proof_lines}
"""

    def _float_env(self, name: str, default: float) -> float:
        try:
            return float(os.getenv(name, str(default)))
        except ValueError:
            return default


engine = SimulationEngine()
