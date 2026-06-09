from __future__ import annotations

import json
import threading
import time
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

from .cognition import AgentCognition
from .models import Agent, DemoBookmark, EventLog, KnowledgeEdge, Location, MemoryEntry, PlanItem, SnapshotStatus, WorldState


class SimulationEngine:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._speed_presets = {
            "0.5x": 4.0,
            "1x": 2.0,
            "2x": 1.0,
        }
        self._active_speed_label = "1x"
        self._tick_interval_seconds = self._speed_presets[self._active_speed_label]
        self._snapshot_bundle: dict | None = None
        self._bookmarks = self._build_bookmarks()
        self._cognition = AgentCognition()
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
            }
            self.shared_pairs: set[tuple[str, str]] = set()
            self._refresh_recent_memories()
            self._ensure_plans()
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
            self.shared_pairs = bundle["shared_pairs"]
            self._active_speed_label = bundle["active_speed_label"]
            self._tick_interval_seconds = self._speed_presets[self._active_speed_label]
            return self._snapshot_status()

    def jump_to_bookmark(self, bookmark_key: str) -> DemoBookmark:
        bookmark = next((item for item in self._bookmarks if item.key == bookmark_key), None)
        if bookmark is None:
            raise ValueError(f"Unsupported bookmark: {bookmark_key}")

        self.reset()
        while self.current_time.strftime("%H:%M") < bookmark.target_time:
            self.tick()

        with self._lock:
            self.running = False
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
            "knowledge_status": snapshot.knowledge_status,
            "knowledge_edges": [edge.model_dump() for edge in snapshot.knowledge_edges],
            "events": [event.model_dump() for event in snapshot.events[:8]],
            "reflections": reflections,
            "selected_proof_points": [
                "Plan-driven movement is visible on the town map.",
                "Dialogue spread is recorded in the event timeline and propagation chain.",
                "Retrieved memories explain why an agent acts in the current context.",
                "Reflection appears only after information becomes shared social knowledge.",
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
                agent.retrieved_memories = retrieved
                agent.retrieval_explanations = retrieval_explanations
                decision = self._cognition.generate_action(
                    agent=agent,
                    active_plan=active_item,
                    current_location=self._location(agent.current_location_id),
                    nearby_agents=nearby_agents,
                    retrieved_memories=retrieved,
                    time_label=time_label,
                )
                agent.current_action = decision.summary
                agent.last_utterance = decision.utterance
                agent.reasoning_note = decision.reasoning_note

            self._run_storyline(time_label)
            self._trim_logs()

    def snapshot(self) -> WorldState:
        with self._lock:
            return WorldState(
                day_label=self.current_time.strftime("%Y-%m-%d"),
                time_label=self.current_time.strftime("%H:%M"),
                running=self.running,
                tick_count=self.tick_count,
                llm_enabled=self._cognition.enabled,
                llm_model=self._cognition.model if self._cognition.enabled else None,
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

    def _run_storyline(self, time_label: str) -> None:
        encounters: dict[str, list[Agent]] = defaultdict(list)
        for agent in self.agents:
            encounters[agent.current_location_id].append(agent)

        for location_id, occupants in encounters.items():
            if len(occupants) < 2:
                continue
            knowers = [agent for agent in occupants if agent.knows_party]
            listeners = [agent for agent in occupants if not agent.knows_party]
            if listeners and knowers:
                for listener in listeners:
                    preferred_speaker = next((agent for agent in knowers if agent.id != "alice"), knowers[0])
                    self._handle_pair_interaction(preferred_speaker, listener, self._location(location_id), time_label)

        if self._party_knowers_count() >= 3 and not self.story_flags["party_reflection_written"]:
            self.story_flags["party_reflection_written"] = True
            reflection_actors: list[str] = []
            for agent in self.agents:
                if agent.knows_party:
                    reflection_actors.append(agent.id)
                    reflection_text = self._cognition.generate_reflection(agent, time_label)
                    reflection = self._memory(
                        "reflection",
                        reflection_text,
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
                    agent.reasoning_note = "A new high-level reflection was formed because the social information spread across the town."
            self._add_event(
                "Reflection formed",
                "The agents now treat Alice's gathering as a shared town event rather than isolated information.",
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

    def _handle_pair_interaction(self, first: Agent, second: Agent, location: Location, time_label: str) -> None:
        if first.knows_party == second.knows_party:
            return

        speaker, listener = (first, second) if first.knows_party else (second, first)
        pair_key = tuple(sorted([speaker.id, listener.id]))
        if pair_key in self.shared_pairs:
            return

        speaker_retrieved, speaker_explanations = self._cognition.retrieve_memories_with_explanations(
            agent=speaker,
            active_plan=self._active_plan_item(speaker, time_label),
            current_location=location,
            nearby_agents=[listener],
            time_label=time_label,
        )
        decision = self._cognition.generate_dialogue(
            speaker=speaker,
            listener=listener,
            current_location=location,
            retrieved_memories=speaker_retrieved,
            time_label=time_label,
        )
        self.shared_pairs.add(pair_key)
        listener_learned_now = decision.listener_learns_party and listener.id not in self.knowledge_status
        listener.knows_party = decision.listener_learns_party or listener.knows_party
        if listener_learned_now:
            self.knowledge_status[listener.id] = time_label
            self.knowledge_edges.append(
                KnowledgeEdge(
                    source_agent_id=speaker.id,
                    target_agent_id=listener.id,
                    learned_at=time_label,
                    tick_count=self.tick_count,
                )
            )
        speaker.current_action = "Sharing a socially relevant update"
        listener.current_action = "Reacting to new social information"
        speaker.last_utterance = decision.speaker_utterance
        listener.last_utterance = decision.listener_utterance
        speaker.reasoning_note = f"{speaker.name} knows the gathering and sees {listener.name} nearby, so the social information is shared."
        listener.reasoning_note = f"{listener.name} received new social information from {speaker.name} during the encounter."
        self._add_event(
            decision.event_title,
            decision.event_detail,
            event_type="share" if decision.listener_learns_party else "conversation",
            actor_ids=[speaker.id, listener.id],
            location_id=location.id,
        )
        self._remember(speaker, "conversation", decision.speaker_memory, location.id, 0.84, [listener.id])
        self._remember(listener, "conversation", decision.listener_memory, location.id, 0.88, [speaker.id])
        speaker.retrieved_memories = speaker_retrieved
        speaker.retrieval_explanations = speaker_explanations
        listener.retrieved_memories, listener.retrieval_explanations = self._cognition.retrieve_memories_with_explanations(
            agent=listener,
            active_plan=self._active_plan_item(listener, time_label),
            current_location=location,
            nearby_agents=[speaker],
            time_label=time_label,
        )

    def _party_knowers_count(self) -> int:
        return sum(1 for agent in self.agents if agent.knows_party)

    def _refresh_recent_memories(self) -> None:
        for agent in self.agents:
            agent.recent_memories = agent.memory_bank[:5]

    def _ensure_plans(self) -> None:
        day_label = self.current_time.strftime("%Y-%m-%d")
        for agent in self.agents:
            generated = self._cognition.generate_plan(agent, self.locations, day_label)
            if generated:
                agent.plan = generated
            agent.active_plan = self._active_plan_item(agent, self.current_time.strftime("%H:%M"))

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


engine = SimulationEngine()
