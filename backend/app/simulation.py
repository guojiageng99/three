from __future__ import annotations

import threading
import time
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timedelta
from uuid import uuid4

from .cognition import AgentCognition
from .models import Agent, EventLog, Location, MemoryEntry, PlanItem, WorldState


class SimulationEngine:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._tick_interval_seconds = 2.0
        self._cognition = AgentCognition()
        self.reset()

    def reset(self) -> None:
        with self._lock:
            self.running = False
            self.current_time = datetime(2026, 6, 4, 8, 0)
            self.tick_count = 0
            self.locations = self._build_locations()
            self.agents = self._build_agents()
            self._refresh_recent_memories()
            self._ensure_plans()
            self.events: list[EventLog] = []
            self.story_flags = {
                "party_reflection_written": False,
            }
            self.shared_pairs: set[tuple[str, str]] = set()
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
                    )
                    self._remember(
                        agent,
                        "observation",
                        f"I moved to {self._location_name(active_item.location_id)} for {active_item.summary}.",
                        active_item.location_id,
                        0.35,
                    )
                nearby_agents = [other for other in self.agents if other.id != agent.id and other.current_location_id == agent.current_location_id]
                retrieved = self._cognition.retrieve_memories(
                    agent=agent,
                    active_plan=active_item,
                    current_location=self._location(agent.current_location_id),
                    nearby_agents=nearby_agents,
                    time_label=time_label,
                )
                agent.retrieved_memories = retrieved
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
            )

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            should_tick = False
            with self._lock:
                should_tick = self.running
            if should_tick:
                self.tick()
            time.sleep(self._tick_interval_seconds)

    def _build_locations(self) -> list[Location]:
        return [
            Location(id="home_alice", name="Alice's Home", x=8, y=18, description="A warm apartment with party notes on the table."),
            Location(id="park", name="Johnson Park", x=42, y=10, description="A calm open park for walking and chance encounters."),
            Location(id="cafe", name="Hobbs Cafe", x=72, y=22, description="A small cafe where agents work and chat."),
            Location(id="square", name="Town Square", x=48, y=46, description="The social center of the town."),
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
            for agent in self.agents:
                if agent.knows_party:
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

    def _agent(self, agent_id: str) -> Agent:
        return next(agent for agent in self.agents if agent.id == agent_id)

    def _handle_pair_interaction(self, first: Agent, second: Agent, location: Location, time_label: str) -> None:
        if first.knows_party == second.knows_party:
            return

        speaker, listener = (first, second) if first.knows_party else (second, first)
        pair_key = tuple(sorted([speaker.id, listener.id]))
        if pair_key in self.shared_pairs:
            return

        retrieved = self._cognition.retrieve_memories(
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
            retrieved_memories=retrieved,
            time_label=time_label,
        )
        self.shared_pairs.add(pair_key)
        listener.knows_party = decision.listener_learns_party or listener.knows_party
        speaker.current_action = "Sharing a socially relevant update"
        listener.current_action = "Reacting to new social information"
        speaker.last_utterance = decision.speaker_utterance
        listener.last_utterance = decision.listener_utterance
        speaker.reasoning_note = f"{speaker.name} knows the gathering and sees {listener.name} nearby, so the social information is shared."
        listener.reasoning_note = f"{listener.name} received new social information from {speaker.name} during the encounter."
        self._add_event(decision.event_title, decision.event_detail)
        self._remember(speaker, "conversation", decision.speaker_memory, location.id, 0.84, [listener.id])
        self._remember(listener, "conversation", decision.listener_memory, location.id, 0.88, [speaker.id])
        speaker.retrieved_memories = retrieved
        listener.retrieved_memories = self._cognition.retrieve_memories(
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

    def _add_event(self, title: str, detail: str) -> None:
        self.events.append(
            EventLog(
                id=uuid4().hex,
                time=self.current_time.strftime("%H:%M"),
                title=title,
                detail=detail,
            )
        )

    def _trim_logs(self) -> None:
        self.events = self.events[-30:]


engine = SimulationEngine()
