"use client";

import { Agent, EventLog } from "@/lib/types";

type SidebarProps = {
  agent: Agent | null;
  currentLocationName: string | null;
  events: EventLog[];
  dayLabel: string;
  timeLabel: string;
  tickCount: number;
  llmEnabled: boolean;
  llmModel: string | null;
};

export function Sidebar({
  agent,
  currentLocationName,
  events,
  dayLabel,
  timeLabel,
  tickCount,
  llmEnabled,
  llmModel,
}: SidebarProps) {
  return (
    <aside className="sidebar">
      <section className="panel status-panel">
        <div className="eyebrow">World State</div>
        <h2>{dayLabel}</h2>
        <p className="time-label">{timeLabel}</p>
        <div className="status-grid">
          <div>
            <span className="status-key">Tick</span>
            <strong>#{tickCount}</strong>
          </div>
          <div>
            <span className="status-key">Mode</span>
            <strong>{llmEnabled ? llmModel : "Fallback"}</strong>
          </div>
        </div>
      </section>

      <section className="panel agent-profile-panel">
        <div className="eyebrow">Selected Agent</div>
        {agent ? (
          <>
            <div className="agent-profile-header">
              <span className="agent-color-chip" style={{ backgroundColor: agent.color }} aria-hidden="true" />
              <div>
                <h3>{agent.name}</h3>
                <p className="agent-role">{agent.role}</p>
              </div>
            </div>
            <p className="agent-summary">{agent.profile_summary}</p>
            <div className="fact-row">
              <span className="fact-pill">{currentLocationName ?? "Unknown location"}</span>
              <span className="fact-pill">{agent.knows_party ? "Knows gathering" : "No gathering knowledge"}</span>
            </div>
            <div className="callout-card">
              <span className="callout-label">Current action</span>
              <p>{agent.current_action}</p>
            </div>
            <div className="callout-card subtle">
              <span className="callout-label">Latest utterance</span>
              <p>{agent.last_utterance ?? "No spoken line in the current context."}</p>
            </div>
          </>
        ) : (
          <p>Select an agent on the map.</p>
        )}
      </section>

      <section className="panel highlight-panel">
        <div className="eyebrow">Reasoning Context</div>
        {agent ? (
          <>
            <div className="callout-card bright">
              <span className="callout-label">Active plan</span>
              <p>{agent.active_plan ? `${agent.active_plan.time_slot} ${agent.active_plan.summary}` : "No active plan"}</p>
            </div>
            <p className="reasoning-copy">{agent.reasoning_note ?? "No explicit reasoning note for the current state."}</p>
          </>
        ) : (
          <p>No agent selected.</p>
        )}
      </section>

      <section className="panel">
        <div className="eyebrow">Active Plan</div>
        {agent ? (
          <ul className="list timeline-list">
            {agent.plan.map((item) => (
              <li
                key={`${agent.id}-${item.time_slot}`}
                className={agent.active_plan?.time_slot === item.time_slot ? "active-plan-row" : undefined}
              >
                <strong>{item.time_slot}</strong> {item.summary}
              </li>
            ))}
          </ul>
        ) : (
          <p>No agent selected.</p>
        )}
      </section>

      <section className="panel">
        <div className="eyebrow">Retrieved Memories</div>
        {agent ? (
          <ul className="list timeline-list">
            {agent.retrieved_memories.length > 0 ? (
              agent.retrieved_memories.map((memory) => (
                <li key={memory.id}>
                  <strong>{memory.timestamp}</strong>
                  <span>{memory.text}</span>
                </li>
              ))
            ) : (
              <li>No retrieved memories in the current context.</li>
            )}
          </ul>
        ) : (
          <p>No agent selected.</p>
        )}
      </section>

      <section className="panel">
        <div className="eyebrow">Recent Memories</div>
        {agent ? (
          <ul className="list timeline-list">
            {agent.recent_memories.map((memory) => (
              <li key={memory.id}>
                <strong>{memory.timestamp}</strong>
                <span>{memory.text}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p>No agent selected.</p>
        )}
      </section>

      <section className="panel">
        <div className="eyebrow">Reflections</div>
        {agent ? (
          <ul className="list reflection-list">
            {agent.reflections.length > 0 ? (
              agent.reflections.map((memory) => <li key={memory.id}>{memory.text}</li>)
            ) : (
              <li>No reflection yet.</li>
            )}
          </ul>
        ) : (
          <p>No agent selected.</p>
        )}
      </section>

      <section className="panel">
        <div className="eyebrow">Event Log</div>
        <ul className="list timeline-list">
          {events.map((event) => (
            <li key={event.id}>
              <strong>{event.time}</strong>
              <span>
                {event.title}: {event.detail}
              </span>
            </li>
          ))}
        </ul>
      </section>
    </aside>
  );
}
