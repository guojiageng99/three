"use client";

import { useEffect, useMemo, useState } from "react";

import { Controls } from "@/components/Controls";
import { Sidebar } from "@/components/Sidebar";
import { TownMap } from "@/components/TownMap";
import { postAction, websocketUrl } from "@/lib/api";
import { WorldState } from "@/lib/types";

export default function HomePage() {
  const [world, setWorld] = useState<WorldState | null>(null);
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);
  const [connectionState, setConnectionState] = useState("connecting");

  useEffect(() => {
    const socket = new WebSocket(websocketUrl());
    socket.onopen = () => setConnectionState("connected");
    socket.onclose = () => setConnectionState("disconnected");
    socket.onerror = () => setConnectionState("error");
    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data) as WorldState;
      setWorld(payload);
      setSelectedAgentId((current) => current ?? payload.agents[0]?.id ?? null);
    };
    return () => socket.close();
  }, []);

  const selectedAgent = useMemo(() => {
    if (!world || !selectedAgentId) {
      return null;
    }
    return world.agents.find((agent) => agent.id === selectedAgentId) ?? null;
  }, [selectedAgentId, world]);

  const selectedLocation = useMemo(() => {
    if (!world || !selectedAgent) {
      return null;
    }
    return world.locations.find((location) => location.id === selectedAgent.current_location_id) ?? null;
  }, [selectedAgent, world]);

  const worldStats = useMemo(() => {
    if (!world) {
      return null;
    }

    const partyAwareCount = world.agents.filter((agent) => agent.knows_party).length;
    const totalReflections = world.agents.reduce((sum, agent) => sum + agent.reflections.length, 0);
    return {
      partyAwareCount,
      totalReflections,
    };
  }, [world]);

  return (
    <main className="shell">
      <section className="masthead">
        <div className="masthead-mark">
          <span className="masthead-dot" aria-hidden="true" />
          Social Simulation Observatory
        </div>
        <div className="masthead-meta">
          <span>Paper reproduction</span>
          <span>3 agents</span>
          <span>4 locations</span>
          <span>Course presentation mode</span>
        </div>
      </section>

      <section className="hero">
        <div className="hero-copy-block">
          <p className="eyebrow">Generative Agents Demo</p>
          <h1>Observe a small town turn private memories into shared social behavior.</h1>
          <p className="hero-copy">
            This course-demo reproduction keeps the paper&apos;s most important loop intact: planning, remembering,
            speaking, spreading information, and reflecting. The interface is tuned for explanation, not just motion.
          </p>
          <div className="story-strip">
            <span>10:00 Alice tells Bob</span>
            <span>14:00 Bob tells Carol</span>
            <span>Shared reflection emerges after the rumor spreads</span>
          </div>
        </div>
        <div className="hero-actions panel control-panel">
          <div className="control-panel-header">
            <div>
              <p className="eyebrow">Simulation Controls</p>
              <h2>Run the town clock</h2>
            </div>
            <span className={`status-pill ${connectionState}`}>{connectionState}</span>
          </div>
          <Controls
            running={world?.running ?? false}
            onStart={() => postAction("/api/sim/start")}
            onPause={() => postAction("/api/sim/pause")}
            onTick={() => postAction("/api/sim/tick")}
            onReset={() => postAction("/api/sim/reset")}
          />
          <p className="control-note">
            Use <strong>Start</strong> for continuous playback, <strong>Single Tick</strong> for step-by-step
            explanation, and <strong>Reset</strong> before recording another take.
          </p>
        </div>
      </section>

      {world && worldStats ? (
        <section className="summary-strip" aria-label="Simulation summary">
          <article className="summary-card">
            <p className="summary-label">Simulation Clock</p>
            <strong>{world.time_label}</strong>
            <span>{world.day_label}</span>
          </article>
          <article className="summary-card">
            <p className="summary-label">Social Spread</p>
            <strong>
              {worldStats.partyAwareCount}/{world.agents.length}
            </strong>
            <span>agents know about the gathering</span>
          </article>
          <article className="summary-card">
            <p className="summary-label">Reflection Load</p>
            <strong>{worldStats.totalReflections}</strong>
            <span>reflection memories accumulated</span>
          </article>
          <article className="summary-card focus-card">
            <p className="summary-label">Current Focus</p>
            <strong>{selectedAgent ? selectedAgent.name : "No agent selected"}</strong>
            <span>
              {selectedAgent && selectedLocation
                ? `${selectedLocation.name} · ${selectedAgent.active_plan?.summary ?? selectedAgent.current_action}`
                : "Select an agent on the map to inspect cognition"}
            </span>
          </article>
        </section>
      ) : null}

      {world ? (
        <section className="content-grid">
          <TownMap
            agents={world.agents}
            locations={world.locations}
            selectedAgentId={selectedAgentId}
            onSelectAgent={setSelectedAgentId}
          />
          <Sidebar
            agent={selectedAgent}
            currentLocationName={selectedLocation?.name ?? null}
            events={world.events}
            dayLabel={world.day_label}
            timeLabel={world.time_label}
            tickCount={world.tick_count}
            llmEnabled={world.llm_enabled}
            llmModel={world.llm_model}
          />
        </section>
      ) : (
        <section className="loading-card">
          <p>Waiting for backend simulation state...</p>
        </section>
      )}
    </main>
  );
}
