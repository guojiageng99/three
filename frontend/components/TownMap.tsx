"use client";

import { Agent, Location } from "@/lib/types";

type TownMapProps = {
  agents: Agent[];
  locations: Location[];
  selectedAgentId: string | null;
  onSelectAgent: (agentId: string) => void;
};

export function TownMap({ agents, locations, selectedAgentId, onSelectAgent }: TownMapProps) {
  const agentsByLocation = new Map<string, Agent[]>();
  for (const agent of agents) {
    const items = agentsByLocation.get(agent.current_location_id) ?? [];
    items.push(agent);
    agentsByLocation.set(agent.current_location_id, items);
  }

  return (
    <div className="map-card">
      <div className="map-header">
        <div>
          <p className="eyebrow">Town Surface</p>
          <h2>Smallville Observation Board</h2>
        </div>
        <p className="map-header-copy">
          Each location hosts the agents currently present there. Click a resident to inspect plan, memory retrieval,
          and reflection state on the right.
        </p>
      </div>
      <div className="map-grid">
        {locations.map((location) => {
          const occupants = agentsByLocation.get(location.id) ?? [];
          return (
            <div
              key={location.id}
              className="location-tile"
              style={{ left: `${location.x}%`, top: `${location.y}%` }}
            >
              <div className="location-topline">
                <div className="location-name">{location.name}</div>
                <span className="occupancy-pill">{occupants.length} here</span>
              </div>
              <div className="location-desc">{location.description}</div>
              <div className="agent-stack">
                {occupants.map((agent) => (
                  <button
                    key={agent.id}
                    className={selectedAgentId === agent.id ? "agent-chip selected" : "agent-chip"}
                    style={{ backgroundColor: agent.color }}
                    onClick={() => onSelectAgent(agent.id)}
                    title={agent.current_action}
                    type="button"
                    aria-pressed={selectedAgentId === agent.id}
                  >
                    <span className="agent-chip-name">{agent.name}</span>
                    <span className="speech">{agent.current_action}</span>
                  </button>
                ))}
              </div>
            </div>
          );
        })}
      </div>
      <div className="map-caption">
        <div className="legend-row">
          {agents.map((agent) => (
            <span className="legend-item" key={agent.id}>
              <span className="legend-swatch" style={{ backgroundColor: agent.color }} aria-hidden="true" />
              {agent.name}
            </span>
          ))}
        </div>
        <p>A compact town view designed for classroom explanation and demo recording.</p>
      </div>
    </div>
  );
}
