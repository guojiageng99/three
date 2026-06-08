from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime

import httpx

from .models import Agent, Location, MemoryEntry, PlanItem
from .prompt_templates import (
    ACTION_SYSTEM_PROMPT,
    DIALOGUE_SYSTEM_PROMPT,
    PLAN_SYSTEM_PROMPT,
    REFLECTION_SYSTEM_PROMPT,
)


@dataclass
class ActionDecision:
    summary: str
    utterance: str | None = None
    reasoning_note: str | None = None


@dataclass
class DialogueDecision:
    event_title: str
    event_detail: str
    speaker_utterance: str
    listener_utterance: str
    speaker_memory: str
    listener_memory: str
    listener_learns_party: bool = False


class AgentCognition:
    def __init__(self) -> None:
        self.api_key = os.getenv("LLM_API_KEY", "").strip()
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.enabled = bool(self.api_key)

    def generate_plan(self, agent: Agent, locations: list[Location], day_label: str) -> list[PlanItem] | None:
        if self.enabled:
            prompt = {
                "day": day_label,
                "agent": {
                    "name": agent.name,
                    "role": agent.role,
                    "personality": agent.personality,
                    "profile_summary": agent.profile_summary,
                    "knows_party": agent.knows_party,
                },
                "available_locations": [
                    {"location_id": location.id, "name": location.name, "description": location.description}
                    for location in locations
                ],
                "existing_reflections": [memory.text for memory in agent.reflections[:3]],
            }
            response = self._chat_json(system_prompt=PLAN_SYSTEM_PROMPT, user_payload=prompt)
            if response:
                items = response.get("plan")
                if isinstance(items, list):
                    valid_location_ids = {location.id for location in locations}
                    parsed: list[PlanItem] = []
                    for item in items[:4]:
                        if not isinstance(item, dict):
                            continue
                        time_slot = str(item.get("time_slot", "")).strip()
                        location_id = str(item.get("location_id", "")).strip()
                        summary = str(item.get("summary", "")).strip()
                        if time_slot and location_id in valid_location_ids and summary:
                            parsed.append(PlanItem(time_slot=time_slot, location_id=location_id, summary=summary))
                    if parsed:
                        parsed.sort(key=lambda plan_item: plan_item.time_slot)
                        return parsed
        return None

    def retrieve_memories(
        self,
        agent: Agent,
        active_plan: PlanItem,
        current_location: Location,
        nearby_agents: list[Agent],
        time_label: str,
        limit: int = 3,
    ) -> list[MemoryEntry]:
        query_terms = self._tokenize(
            " ".join(
                [
                    active_plan.summary,
                    current_location.name,
                    current_location.description,
                    "party gathering invite social town" if agent.knows_party else "",
                    " ".join(other.name for other in nearby_agents),
                ]
            )
        )
        scored: list[tuple[float, MemoryEntry]] = []
        for memory in agent.memory_bank:
            overlap = len(query_terms.intersection(self._tokenize(memory.text)))
            location_bonus = 0.18 if memory.location_id == current_location.id else 0.0
            social_bonus = 0.08 * sum(1 for other in nearby_agents if other.id in memory.related_agents)
            recency_bonus = self._recency_score(memory.timestamp, time_label)
            score = memory.importance * 0.45 + recency_bonus * 0.2 + location_bonus + social_bonus + overlap * 0.06
            scored.append((score, memory))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [memory for _, memory in scored[:limit]]

    def generate_action(
        self,
        agent: Agent,
        active_plan: PlanItem,
        current_location: Location,
        nearby_agents: list[Agent],
        retrieved_memories: list[MemoryEntry],
        time_label: str,
    ) -> ActionDecision:
        if self.enabled:
            prompt = {
                "time": time_label,
                "agent": {
                    "name": agent.name,
                    "role": agent.role,
                    "personality": agent.personality,
                    "profile_summary": agent.profile_summary,
                    "knows_party": agent.knows_party,
                },
                "plan": active_plan.model_dump(),
                "location": current_location.model_dump(),
                "nearby_agents": [other.name for other in nearby_agents],
                "retrieved_memories": [memory.text for memory in retrieved_memories],
                "instruction": "Return compact JSON with keys summary and utterance. Keep the action concrete and visible for a UI demo.",
            }
            response = self._chat_json(
                system_prompt=ACTION_SYSTEM_PROMPT,
                user_payload=prompt,
            )
            if response:
                summary = str(response.get("summary", "")).strip()
                utterance = self._normalize_optional_text(response.get("utterance"))
                if summary:
                    return ActionDecision(
                        summary=summary,
                        utterance=utterance,
                        reasoning_note=self._build_reasoning_note(active_plan, current_location, nearby_agents, retrieved_memories),
                    )

        return self._fallback_action(agent, active_plan, current_location, nearby_agents, retrieved_memories)

    def generate_dialogue(
        self,
        speaker: Agent,
        listener: Agent,
        current_location: Location,
        retrieved_memories: list[MemoryEntry],
        time_label: str,
    ) -> DialogueDecision:
        if self.enabled:
            prompt = {
                "time": time_label,
                "location": current_location.name,
                "speaker": {
                    "name": speaker.name,
                    "role": speaker.role,
                    "personality": speaker.personality,
                    "knows_party": speaker.knows_party,
                },
                "listener": {
                    "name": listener.name,
                    "role": listener.role,
                    "personality": listener.personality,
                    "knows_party": listener.knows_party,
                },
                "retrieved_memories": [memory.text for memory in retrieved_memories],
                "instruction": (
                    "Return JSON with event_title, event_detail, speaker_utterance, listener_utterance, "
                    "speaker_memory, listener_memory, listener_learns_party. The dialogue should stay natural, short, "
                    "and centered on whether the listener learns about Alice's evening gathering."
                ),
            }
            response = self._chat_json(
                system_prompt=DIALOGUE_SYSTEM_PROMPT,
                user_payload=prompt,
            )
            if response:
                try:
                    return DialogueDecision(
                        event_title=str(response.get("event_title", "Conversation")).strip() or "Conversation",
                        event_detail=str(response.get("event_detail", "")).strip() or f"{speaker.name} and {listener.name} talk in town.",
                        speaker_utterance=str(response.get("speaker_utterance", "")).strip() or f"{speaker.name} starts a short conversation.",
                        listener_utterance=str(response.get("listener_utterance", "")).strip() or f"{listener.name} responds politely.",
                        speaker_memory=str(response.get("speaker_memory", "")).strip() or f"I talked with {listener.name}.",
                        listener_memory=str(response.get("listener_memory", "")).strip() or f"I talked with {speaker.name}.",
                        listener_learns_party=bool(response.get("listener_learns_party", False)),
                    )
                except Exception:
                    pass

        return self._fallback_dialogue(speaker, listener, current_location, time_label)

    def generate_reflection(self, agent: Agent, time_label: str) -> str:
        source_memories = agent.memory_bank[:5]
        if self.enabled and source_memories:
            prompt = {
                "time": time_label,
                "agent": agent.name,
                "recent_memories": [memory.text for memory in source_memories],
            }
            response = self._chat_json(
                system_prompt=REFLECTION_SYSTEM_PROMPT,
                user_payload=prompt,
            )
            if response:
                reflection = str(response.get("reflection", "")).strip()
                if reflection:
                    return reflection

        if agent.knows_party:
            return "Alice's gathering is turning into a shared town event, and I should factor it into later social choices."
        return "Recent encounters suggest the town's social rhythm is driven by repeated meetings at the same few places."

    def _fallback_action(
        self,
        agent: Agent,
        active_plan: PlanItem,
        current_location: Location,
        nearby_agents: list[Agent],
        retrieved_memories: list[MemoryEntry],
    ) -> ActionDecision:
        if agent.knows_party and any("gathering" in memory.text.lower() or "party" in memory.text.lower() for memory in retrieved_memories):
            if nearby_agents:
                return ActionDecision(
                    summary=f"Following the plan at {current_location.name} while thinking about tonight's gathering",
                    utterance=f"I should mention tonight's gathering to {nearby_agents[0].name} if the moment feels natural.",
                    reasoning_note=self._build_reasoning_note(active_plan, current_location, nearby_agents, retrieved_memories),
                )
            return ActionDecision(
                summary=f"Following the plan at {current_location.name} and mentally tracking tonight's gathering",
                utterance="Tonight's gathering is starting to shape the day.",
                reasoning_note=self._build_reasoning_note(active_plan, current_location, nearby_agents, retrieved_memories),
            )
        return ActionDecision(
            summary=active_plan.summary,
            utterance=f"I am at {current_location.name}, focused on {active_plan.summary.lower()}.",
            reasoning_note=self._build_reasoning_note(active_plan, current_location, nearby_agents, retrieved_memories),
        )

    def _fallback_dialogue(
        self,
        speaker: Agent,
        listener: Agent,
        current_location: Location,
        time_label: str,
    ) -> DialogueDecision:
        if speaker.knows_party and not listener.knows_party:
            return DialogueDecision(
                event_title="Party invitation shared",
                event_detail=f"At {current_location.name} around {time_label}, {speaker.name} tells {listener.name} about Alice's evening gathering.",
                speaker_utterance="Alice is hosting a small gathering tonight. You should stop by if you're free.",
                listener_utterance="That sounds nice. I didn't know about it, but now I'm curious.",
                speaker_memory=f"I told {listener.name} about the gathering tonight.",
                listener_memory=f"{speaker.name} told me about Alice's gathering tonight.",
                listener_learns_party=True,
            )
        return DialogueDecision(
            event_title="Casual social exchange",
            event_detail=f"{speaker.name} and {listener.name} exchange a few thoughts at {current_location.name}.",
            speaker_utterance="The town feels especially connected today.",
            listener_utterance="It does. The same places keep bringing people together.",
            speaker_memory=f"I had a short conversation with {listener.name} at {current_location.name}.",
            listener_memory=f"I had a short conversation with {speaker.name} at {current_location.name}.",
            listener_learns_party=listener.knows_party,
        )

    def _chat_json(self, system_prompt: str, user_payload: dict) -> dict | None:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model,
            "temperature": 0.4,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
            ],
        }
        try:
            with httpx.Client(timeout=12.0) as client:
                response = client.post(f"{self.base_url}/chat/completions", headers=headers, json=body)
                response.raise_for_status()
                payload = response.json()
        except Exception:
            return None

        try:
            content = payload["choices"][0]["message"]["content"]
        except Exception:
            return None
        if isinstance(content, list):
            content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
        cleaned = self._strip_code_fence(str(content))
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.S)
            if not match:
                return None
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None

    def _build_reasoning_note(
        self,
        active_plan: PlanItem,
        current_location: Location,
        nearby_agents: list[Agent],
        retrieved_memories: list[MemoryEntry],
    ) -> str:
        memory_hint = retrieved_memories[0].text if retrieved_memories else "No strong memory cue."
        nearby = ", ".join(agent.name for agent in nearby_agents) if nearby_agents else "No nearby agents"
        return (
            f"Plan focus: {active_plan.summary}. "
            f"Location: {current_location.name}. "
            f"Nearby: {nearby}. "
            f"Top memory cue: {memory_hint}"
        )

    def _strip_code_fence(self, text: str) -> str:
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z0-9_-]*", "", text).strip()
            if text.endswith("```"):
                text = text[:-3].strip()
        return text

    def _normalize_optional_text(self, value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _tokenize(self, text: str) -> set[str]:
        return {token for token in re.findall(r"[a-zA-Z']+", text.lower()) if len(token) > 2}

    def _recency_score(self, memory_timestamp: str, current_time: str) -> float:
        try:
            memory_dt = datetime.strptime(memory_timestamp, "%H:%M")
            current_dt = datetime.strptime(current_time, "%H:%M")
        except ValueError:
            return 0.0
        delta_minutes = max((current_dt - memory_dt).total_seconds() / 60.0, 0.0)
        if delta_minutes <= 30:
            return 1.0
        if delta_minutes <= 120:
            return 0.7
        if delta_minutes <= 300:
            return 0.4
        return 0.15
