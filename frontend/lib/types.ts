export type Location = {
  id: string;
  name: string;
  x: number;
  y: number;
  description: string;
};

export type PlanItem = {
  time_slot: string;
  location_id: string;
  summary: string;
};

export type MemoryEntry = {
  id: string;
  type: string;
  text: string;
  timestamp: string;
  location_id: string;
  importance: number;
  related_agents: string[];
};

export type RetrievalExplanation = {
  memory_id: string;
  total_score: number;
  importance_score: number;
  recency_score: number;
  relevance_score: number;
  location_bonus: number;
  social_bonus: number;
  keyword_overlap_count: number;
  explanation_tags: string[];
};

export type Agent = {
  id: string;
  name: string;
  role: string;
  personality: string;
  color: string;
  current_location_id: string;
  current_action: string;
  last_utterance: string | null;
  knows_party: boolean;
  profile_summary: string;
  plan: PlanItem[];
  active_plan: PlanItem | null;
  recent_memories: MemoryEntry[];
  retrieved_memories: MemoryEntry[];
  retrieval_explanations: RetrievalExplanation[];
  reflections: MemoryEntry[];
  reasoning_note: string | null;
};

export type EventLog = {
  id: string;
  time: string;
  title: string;
  detail: string;
  event_type: string;
  actor_ids: string[];
  location_id: string | null;
  tick_count: number;
};

export type KnowledgeEdge = {
  source_agent_id: string;
  target_agent_id: string;
  learned_at: string;
  tick_count: number;
};

export type SnapshotStatus = {
  exists: boolean;
  label: string | null;
  tick_count: number | null;
};

export type DemoBookmark = {
  key: string;
  label: string;
  target_time: string;
  description: string;
};

export type WorldState = {
  day_label: string;
  time_label: string;
  running: boolean;
  tick_count: number;
  simulation_mode: string;
  llm_enabled: boolean;
  llm_provider: string | null;
  llm_model: string | null;
  last_llm_call_status: string;
  reflection_trigger_reason: string | null;
  memory_stream_count: number;
  locations: Location[];
  agents: Agent[];
  events: EventLog[];
  knowledge_edges: KnowledgeEdge[];
  knowledge_status: Record<string, string>;
  active_speed_label: string;
  available_speed_labels: string[];
  available_bookmarks: DemoBookmark[];
  snapshot_status: SnapshotStatus;
};
