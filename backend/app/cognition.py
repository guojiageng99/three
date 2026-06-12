from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from time import perf_counter

import httpx

from .models import Agent, Location, MemoryEntry, PlanItem, RetrievalExplanation
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
    def __init__(self, simulation_mode: str | None = None) -> None:
        configured_mode = (simulation_mode or os.getenv("SIMULATION_MODE", "deterministic")).strip().lower()
        self.simulation_mode = configured_mode if configured_mode in {"deterministic", "llm"} else "deterministic"
        self.api_key = os.getenv("LLM_API_KEY", "").strip()
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.enabled = self.simulation_mode == "llm" and bool(self.api_key)
        self.timeout_seconds = self._float_env("LLM_TIMEOUT_SECONDS", 60.0)
        self.debug_log_enabled = self._truthy_env("LLM_DEBUG_LOG")
        self.log_file = self._resolve_log_file(os.getenv("LLM_LOG_FILE", "backend/logs/llm_debug.log"))
        self.last_llm_call_status = self._initial_llm_status()

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
        memories, _ = self.retrieve_memories_with_explanations(
            agent=agent,
            active_plan=active_plan,
            current_location=current_location,
            nearby_agents=nearby_agents,
            time_label=time_label,
            limit=limit,
        )
        return memories

    def retrieve_memories_with_explanations(
        self,
        agent: Agent,
        active_plan: PlanItem,
        current_location: Location,
        nearby_agents: list[Agent],
        time_label: str,
        limit: int = 3,
    ) -> tuple[list[MemoryEntry], list[RetrievalExplanation]]:
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
        scored: list[tuple[float, MemoryEntry, RetrievalExplanation]] = []
        for memory in agent.memory_bank:
            overlap = len(query_terms.intersection(self._tokenize(memory.text)))
            importance_score = memory.importance * 0.45
            location_bonus = 0.18 if memory.location_id == current_location.id else 0.0
            social_bonus = 0.08 * sum(1 for other in nearby_agents if other.id in memory.related_agents)
            recency_bonus = self._recency_score(memory.timestamp, time_label)
            recency_score = recency_bonus * 0.2
            keyword_score = overlap * 0.06
            relevance_score = keyword_score
            score = importance_score + recency_score + relevance_score + location_bonus + social_bonus
            explanation = RetrievalExplanation(
                memory_id=memory.id,
                total_score=round(score, 4),
                importance_score=round(importance_score, 4),
                recency_score=round(recency_score, 4),
                relevance_score=round(relevance_score, 4),
                location_bonus=round(location_bonus, 4),
                social_bonus=round(social_bonus, 4),
                keyword_overlap_count=overlap,
                explanation_tags=self._explanation_tags(
                    importance_score=importance_score,
                    recency_score=recency_score,
                    location_bonus=location_bonus,
                    social_bonus=social_bonus,
                    overlap=overlap,
                ),
            )
            scored.append((score, memory, explanation))
        scored.sort(key=lambda item: item[0], reverse=True)
        chosen = scored[:limit]
        return [memory for _, memory, _ in chosen], [explanation for _, _, explanation in chosen]

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
        if not self.enabled:
            self.last_llm_call_status = self._initial_llm_status()
            return None

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
        request_url = f"{self.base_url}/chat/completions"
        started_at = perf_counter()
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(request_url, headers=headers, json=body)
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPStatusError as exc:
            self._write_llm_debug_log(
                "request_failed",
                request_url,
                error_type=type(exc).__name__,
                error=str(exc),
                http_status=exc.response.status_code,
                response_body=self._truncate(exc.response.text),
                elapsed_ms=self._elapsed_ms(started_at),
            )
            self.last_llm_call_status = "fallback: llm_request_failed"
            return None
        except Exception as exc:
            self._write_llm_debug_log(
                "request_failed",
                request_url,
                error_type=type(exc).__name__,
                error=str(exc),
                elapsed_ms=self._elapsed_ms(started_at),
            )
            self.last_llm_call_status = "fallback: llm_request_failed"
            return None

        try:
            content = payload["choices"][0]["message"]["content"]
        except Exception as exc:
            self._write_llm_debug_log(
                "invalid_llm_response",
                request_url,
                error_type=type(exc).__name__,
                error=str(exc),
                response_body=self._truncate(json.dumps(payload, ensure_ascii=False)),
                elapsed_ms=self._elapsed_ms(started_at),
            )
            self.last_llm_call_status = "fallback: invalid_llm_response"
            return None
        if isinstance(content, list):
            content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
        cleaned = self._strip_code_fence(str(content))
        try:
            parsed = json.loads(cleaned)
            self._write_llm_debug_log("ok", request_url, response_parse="direct_json", elapsed_ms=self._elapsed_ms(started_at))
            self.last_llm_call_status = "ok"
            return parsed
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.S)
            if not match:
                self._write_llm_debug_log(
                    "invalid_json",
                    request_url,
                    response_body=self._truncate(cleaned),
                    parse_strategy="direct_json",
                    elapsed_ms=self._elapsed_ms(started_at),
                )
                self.last_llm_call_status = "fallback: invalid_json"
                return None
            try:
                parsed = json.loads(match.group(0))
                self._write_llm_debug_log(
                    "ok",
                    request_url,
                    response_parse="json_object_extracted",
                    elapsed_ms=self._elapsed_ms(started_at),
                )
                self.last_llm_call_status = "ok"
                return parsed
            except json.JSONDecodeError:
                self._write_llm_debug_log(
                    "invalid_json",
                    request_url,
                    response_body=self._truncate(cleaned),
                    parse_strategy="json_object_extracted",
                    elapsed_ms=self._elapsed_ms(started_at),
                )
                self.last_llm_call_status = "fallback: invalid_json"
                return None

    def _truthy_env(self, name: str) -> bool:
        return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}

    def _float_env(self, name: str, default: float) -> float:
        raw = os.getenv(name)
        if raw is None or not raw.strip():
            return default
        try:
            value = float(raw)
        except ValueError:
            return default
        return value if value > 0 else default

    def _resolve_log_file(self, raw_path: str | None) -> Path:
        backend_root = Path(__file__).resolve().parents[1]
        repo_root = backend_root.parent
        path = Path((raw_path or "backend/logs/llm_debug.log").strip() or "backend/logs/llm_debug.log")
        if path.is_absolute():
            return path
        if path.parts and path.parts[0].lower() == "backend":
            return repo_root / path
        return backend_root / path

    def _write_llm_debug_log(self, status: str, request_url: str, **fields: object) -> None:
        if not self.debug_log_enabled:
            return
        record = {
            "time": datetime.now().isoformat(timespec="seconds"),
            "status": status,
            "url": request_url,
            "model": self.model,
            "simulation_mode": self.simulation_mode,
            "api_key_present": bool(self.api_key),
            "timeout_seconds": self.timeout_seconds,
            "http_proxy_present": bool(os.getenv("HTTP_PROXY") or os.getenv("http_proxy")),
            "https_proxy_present": bool(os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")),
            **fields,
        }
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with self.log_file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception:
            return

    def _truncate(self, text: str, limit: int = 2000) -> str:
        if len(text) <= limit:
            return text
        return text[:limit] + "...<truncated>"

    def _elapsed_ms(self, started_at: float) -> int:
        return int((perf_counter() - started_at) * 1000)

    def _initial_llm_status(self) -> str:
        if self.simulation_mode != "llm":
            return "disabled: deterministic_mode"
        if not self.api_key:
            return "disabled: missing_api_key"
        return "ready"

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

    def _explanation_tags(
        self,
        importance_score: float,
        recency_score: float,
        location_bonus: float,
        social_bonus: float,
        overlap: int,
    ) -> list[str]:
        tags: list[str] = []
        if importance_score >= 0.3:
            tags.append("high importance")
        if recency_score >= 0.14:
            tags.append("recent")
        if location_bonus > 0:
            tags.append("same location")
        if social_bonus > 0:
            tags.append("related to nearby agent")
        if overlap >= 2:
            tags.append("keyword overlap")
        if not tags:
            tags.append("baseline relevance")
        return tags

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
