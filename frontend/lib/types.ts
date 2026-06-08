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
  reflections: MemoryEntry[];
  reasoning_note: string | null;
};

export type EventLog = {
  id: string;
  time: string;
  title: string;
  detail: string;
};

export type WorldState = {
  day_label: string;
  time_label: string;
  running: boolean;
  tick_count: number;
  llm_enabled: boolean;
  llm_model: string | null;
  locations: Location[];
  agents: Agent[];
  events: EventLog[];
};
