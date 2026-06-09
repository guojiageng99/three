"use client";

import { useEffect, useMemo, useState } from "react";

import { Controls } from "@/components/Controls";
import { Sidebar } from "@/components/Sidebar";
import { TownMap } from "@/components/TownMap";
import {
  jumpToSimulationBookmark,
  loadSimulationSnapshot,
  postAction,
  saveSimulationSnapshot,
  setSimulationSpeed,
  websocketUrl,
} from "@/lib/api";
import { WorldState } from "@/lib/types";

type DemoPhase = {
  label: string;
  headline: string;
  explanation: string;
  presenterCue: string;
  nextFocus: string;
  progressValue: number;
};

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

  const demoPhase = useMemo<DemoPhase | null>(() => {
    if (!world || !worldStats) {
      return null;
    }

    if (worldStats.totalReflections > 0) {
      return {
        label: "反思形成",
        headline: "此时，聚会已经从个体记忆演化为全镇共享的社会认知。",
        explanation: "三位核心角色都知道了这件事，系统也生成了更高层次的反思记忆。",
        presenterCue: "建议在这里暂停，重点解释：反思不是单条记忆，而是系统从多次社会互动中总结出的更高层判断。",
        nextFocus: "查看右侧的反思与推理面板，说明高层记忆是如何出现的。",
        progressValue: 100,
      };
    }

    if (worldStats.partyAwareCount >= 3) {
      return {
        label: "传播完成",
        headline: "聚会信息已经传播到所有核心角色。",
        explanation: "这时它不再是 Alice 的私人信息，而是整个小镇中的共享事件。",
        presenterCue: "建议指向传播链和时间线，说明局部对话如何累积成全局状态变化。",
        nextFocus: "同时观察传播面板和时间线，准备过渡到反思阶段。",
        progressValue: 82,
      };
    }

    if (worldStats.partyAwareCount === 2) {
      return {
        label: "开始传播",
        headline: "第一次有效传播已经发生，信息不再只属于 Alice。",
        explanation: "至少有一位听众获得了新信息，因此现在最适合展示记忆检索、对话生成和知识更新之间的关系。",
        presenterCue: "建议强调这一刻：一次局部对话让另一个角色的内部状态发生了改变。",
        nextFocus: "点击刚刚获得信息的角色，查看他的检索记忆和最新话语。",
        progressValue: 52,
      };
    }

    return {
      label: "初始准备",
      headline: "目前只有 Alice 知道今晚的聚会安排。",
      explanation: "这是最干净的起点，系统已经准备好，但社会传播还没有发生。",
      presenterCue: "建议先使用单步推进，让老师清楚看到第一次信息传播，而不是一开始就自动播放。",
      nextFocus: "先关注地图上 Alice 和 Bob 的相遇时刻。",
      progressValue: 22,
    };
  }, [world, worldStats]);

  const latestEvent = world?.events[0] ?? null;
  const recommendedControlHint = useMemo(() => {
    if (!world || !demoPhase) {
      return "先连接后端，进入演示状态。";
    }
    if (world.running) {
      return "当时间线出现传播或反思事件时，建议立刻暂停并讲解状态变化。";
    }
    if (demoPhase.label === "初始准备") {
      return "建议先用单步推进，这是讲第一次传播最清楚的方式。";
    }
    if (demoPhase.label === "反思形成") {
      return "如果要重新讲一遍，可以直接重置场景或恢复到之前保存的快照。";
    }
    return "可以短时间自动播放，一旦出现关键事件就暂停讲解。";
  }, [world, demoPhase]);

  return (
    <main className="shell">
      <section className="masthead">
        <div className="masthead-mark">
          <span className="masthead-dot" aria-hidden="true" />
          社会传播观测台
        </div>
        <div className="masthead-meta">
          <span>课程复现演示</span>
          <span>3 个角色</span>
          <span>4 个地点</span>
          <span>答辩讲解模式</span>
        </div>
      </section>

      <section className="hero">
        <div className="hero-copy-block">
          <p className="eyebrow">Generative Agents 演示</p>
          <h1>观察一个小镇如何把个体记忆逐步演化成共享的社会行为。</h1>
          <p className="hero-copy">
            这个课程演示版保留了论文里最关键的闭环：计划、记忆、对话、信息传播与反思。界面不是只为了“动起来”，而是为了让老师能看懂内部机制。
          </p>
          <div className="story-strip">
            <span>10:00 Alice 告诉 Bob</span>
            <span>14:00 Bob 再告诉 Carol</span>
            <span>信息传播完成后触发共享反思</span>
          </div>
        </div>
        <div className="hero-actions panel control-panel">
          <div className="control-panel-header">
            <div>
              <p className="eyebrow">演示控制</p>
              <h2>控制小镇时间线</h2>
            </div>
            <span className={`status-pill ${connectionState}`}>{connectionState}</span>
          </div>
          <Controls
            running={world?.running ?? false}
            onStart={() => postAction("/api/sim/start")}
            onPause={() => postAction("/api/sim/pause")}
            onTick={() => postAction("/api/sim/tick")}
            onReset={() => postAction("/api/sim/reset")}
            onSaveSnapshot={() => saveSimulationSnapshot()}
            onLoadSnapshot={() => loadSimulationSnapshot()}
            onSetSpeed={(speedLabel) => setSimulationSpeed(speedLabel)}
            onJumpToBookmark={(bookmarkKey) => jumpToSimulationBookmark(bookmarkKey)}
            activeSpeedLabel={world?.active_speed_label ?? "1x"}
            availableSpeedLabels={world?.available_speed_labels ?? ["0.5x", "1x", "2x"]}
            availableBookmarks={world?.available_bookmarks ?? []}
            snapshotExists={world?.snapshot_status.exists ?? false}
          />
          <p className="control-note">
            建议先用<strong>单步推进</strong>展示第一次传播，再根据讲解节奏切换速度；录屏或答辩前可以先保存快照，避免重来。
          </p>
        </div>
      </section>

      {world && demoPhase ? (
        <section className="guide-grid" aria-label="Presentation guidance">
          <article className="guide-card phase-card">
            <p className="summary-label">Current Phase</p>
            <div className="phase-topline">
              <strong>{demoPhase.label}</strong>
              <span className="phase-meter-label">{demoPhase.progressValue}%</span>
            </div>
            <p className="guide-headline">{demoPhase.headline}</p>
            <p className="guide-copy">{demoPhase.explanation}</p>
            <div className="phase-meter" aria-hidden="true">
              <span style={{ width: `${demoPhase.progressValue}%` }} />
            </div>
          </article>

          <article className="guide-card cue-card">
            <p className="summary-label">Teacher Cue</p>
            <p className="guide-headline">{demoPhase.presenterCue}</p>
            <p className="guide-copy">{recommendedControlHint}</p>
            <div className="cue-footer">
              <span className="cue-kicker">Next focus</span>
              <strong>{demoPhase.nextFocus}</strong>
            </div>
          </article>

          <article className="guide-card event-card">
            <p className="summary-label">Latest Event</p>
            {latestEvent ? (
              <>
                <div className="event-spotlight-topline">
                  <strong>{latestEvent.title}</strong>
                  <span className={`event-type-pill spotlight ${latestEvent.event_type}`}>{latestEvent.event_type}</span>
                </div>
                <p className="guide-copy">{latestEvent.detail}</p>
                <p className="micro-copy">
                  {latestEvent.time} · tick #{latestEvent.tick_count}
                </p>
              </>
            ) : (
              <p className="guide-copy">No event has been emitted yet.</p>
            )}
          </article>
        </section>
      ) : null}

      {world && worldStats ? (
        <section className="summary-strip" aria-label="Simulation summary">
          <article className="summary-card">
            <p className="summary-label">当前时间</p>
            <strong>{world.time_label}</strong>
            <span>{world.day_label}</span>
          </article>
          <article className="summary-card">
            <p className="summary-label">传播进度</p>
            <strong>
              {worldStats.partyAwareCount}/{world.agents.length}
            </strong>
            <span>名角色已经知道聚会信息</span>
          </article>
          <article className="summary-card">
            <p className="summary-label">反思数量</p>
            <strong>{worldStats.totalReflections}</strong>
            <span>条反思记忆已生成</span>
          </article>
          <article className="summary-card focus-card">
            <p className="summary-label">当前观察对象</p>
            <strong>{selectedAgent ? selectedAgent.name : "尚未选择角色"}</strong>
            <span>
              {selectedAgent && selectedLocation
                ? `${selectedLocation.name} · ${selectedAgent.active_plan?.summary ?? selectedAgent.current_action}`
                : "请在地图上选择一个角色查看其认知过程"}
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
            phaseLabel={demoPhase?.label ?? null}
          />
          <Sidebar
            agent={selectedAgent}
            currentLocationName={selectedLocation?.name ?? null}
            events={world.events}
            knowledgeEdges={world.knowledge_edges}
            knowledgeStatus={world.knowledge_status}
            dayLabel={world.day_label}
            timeLabel={world.time_label}
            tickCount={world.tick_count}
            llmEnabled={world.llm_enabled}
            llmModel={world.llm_model}
            activeSpeedLabel={world.active_speed_label}
            snapshotStatus={world.snapshot_status}
            latestEvent={latestEvent}
            phaseLabel={demoPhase?.label ?? null}
            presenterCue={demoPhase?.presenterCue ?? null}
            nextFocus={demoPhase?.nextFocus ?? null}
          />
        </section>
      ) : (
        <section className="loading-card">
          <p>正在等待后端仿真状态...</p>
        </section>
      )}
    </main>
  );
}
