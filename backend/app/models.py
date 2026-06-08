from __future__ import annotations

from pydantic import BaseModel, Field


class Location(BaseModel):
    id: str
    name: str
    x: int
    y: int
    description: str


class PlanItem(BaseModel):
    time_slot: str
    location_id: str
    summary: str


class MemoryEntry(BaseModel):
    id: str
    type: str
    text: str
    timestamp: str
    location_id: str
    importance: float = Field(ge=0.0, le=1.0)
    related_agents: list[str] = Field(default_factory=list)


class RetrievalExplanation(BaseModel):
    memory_id: str
    total_score: float
    importance_score: float
    recency_score: float
    location_bonus: float
    social_bonus: float
    keyword_overlap_count: int
    explanation_tags: list[str] = Field(default_factory=list)


class Agent(BaseModel):
    id: str
    name: str
    role: str
    personality: str
    color: str
    current_location_id: str
    current_action: str
    last_utterance: str | None = None
    knows_party: bool = False
    profile_summary: str
    plan: list[PlanItem] = Field(default_factory=list)
    active_plan: PlanItem | None = None
    memory_bank: list[MemoryEntry] = Field(default_factory=list, exclude=True)
    recent_memories: list[MemoryEntry] = Field(default_factory=list)
    retrieved_memories: list[MemoryEntry] = Field(default_factory=list)
    retrieval_explanations: list[RetrievalExplanation] = Field(default_factory=list)
    reflections: list[MemoryEntry] = Field(default_factory=list)
    reasoning_note: str | None = None


class EventLog(BaseModel):
    id: str
    time: str
    title: str
    detail: str
    event_type: str = "system"
    actor_ids: list[str] = Field(default_factory=list)
    location_id: str | None = None
    tick_count: int = 0


class KnowledgeEdge(BaseModel):
    source_agent_id: str
    target_agent_id: str
    learned_at: str
    tick_count: int


class SnapshotStatus(BaseModel):
    exists: bool
    label: str | None = None
    tick_count: int | None = None


class WorldState(BaseModel):
    day_label: str
    time_label: str
    running: bool
    tick_count: int
    llm_enabled: bool
    llm_model: str | None = None
    locations: list[Location]
    agents: list[Agent]
    events: list[EventLog]
    knowledge_edges: list[KnowledgeEdge] = Field(default_factory=list)
    knowledge_status: dict[str, str] = Field(default_factory=dict)
    active_speed_label: str = "1x"
    available_speed_labels: list[str] = Field(default_factory=list)
    snapshot_status: SnapshotStatus = Field(default_factory=lambda: SnapshotStatus(exists=False))
