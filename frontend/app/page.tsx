"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { Controls } from "@/components/Controls";
import { Sidebar } from "@/components/Sidebar";
import { TownMap } from "@/components/TownMap";
import {
  getSimulationState,
  jumpToSimulationBookmark,
  loadSimulationSnapshot,
  postAction,
  saveSimulationSnapshot,
  setSimulationSpeed,
  websocketUrl,
} from "@/lib/api";
import { formatEventDetail, formatEventTitle, formatEventTypeLabel, formatLocationName, formatPlanSummary } from "@/lib/presenter";
import { WorldState } from "@/lib/types";

type DemoPhase = {
  label: string;
  headline: string;
  explanation: string;
  presenterCue: string;
  nextFocus: string;
  progressValue: number;
};

type StepGuide = {
  label: string;
  observe: string;
  proof: string;
  operatorHint: string;
};

const INITIAL_BOOKMARK_KEY = "initial";
const bookmarkKeyByTimeLabel: Record<string, string> = {
  "08:00": "initial",
  "10:00": "first_spread",
  "14:00": "second_spread",
  "14:30": "reflection",
};

const recommendedAgentByBookmark: Record<string, string> = {
  initial: "alice",
  first_spread: "bob",
  second_spread: "carol",
  reflection: "alice",
};

function inferActiveBookmarkKey(world: WorldState | null): string | null {
  if (!world) {
    return null;
  }
  return bookmarkKeyByTimeLabel[world.time_label] ?? null;
}

function needsFirstTimeReset(world: WorldState): boolean {
  const knowsCount = world.agents.filter((agent) => agent.knows_party).length;
  const hasReflection = world.agents.some((agent) => agent.reflections.length > 0);
  return world.time_label !== "08:00" || world.tick_count !== 0 || knowsCount !== 1 || hasReflection;
}

function recommendedAgentIdForWorld(world: WorldState, bookmarkKey: string | null): string | null {
  if (bookmarkKey) {
    return recommendedAgentByBookmark[bookmarkKey] ?? null;
  }
  if (world.agents.some((agent) => agent.reflections.length > 0)) {
    return "alice";
  }
  if (world.knowledge_status.carol) {
    return "carol";
  }
  if (world.knowledge_status.bob) {
    return "bob";
  }
  return "alice";
}

function recommendedAgentIdForBookmark(bookmarkKey: string): string | null {
  return recommendedAgentByBookmark[bookmarkKey] ?? null;
}

export default function HomePage() {
  const [world, setWorld] = useState<WorldState | null>(null);
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);
  const [connectionState, setConnectionState] = useState("connecting");
  const [actionFeedback, setActionFeedback] = useState<string | null>(null);
  const [activeBookmarkKey, setActiveBookmarkKey] = useState<string | null>(null);
  const didAutoPrepare = useRef(false);
  const pendingBookmarkKey = useRef<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const applyWorldState = (payload: WorldState) => {
      if (!isMounted) {
        return;
      }
      setWorld(payload);
      const inferredBookmarkKey = inferActiveBookmarkKey(payload);
      setActiveBookmarkKey(inferredBookmarkKey);
      setSelectedAgentId((current) => {
        const pendingBookmark = pendingBookmarkKey.current;
        if (pendingBookmark) {
          return recommendedAgentIdForWorld(payload, pendingBookmark) ?? current ?? payload.agents[0]?.id ?? null;
        }
        return current ?? recommendedAgentIdForWorld(payload, inferredBookmarkKey) ?? payload.agents[0]?.id ?? null;
      });
      if (pendingBookmarkKey.current && inferredBookmarkKey === pendingBookmarkKey.current) {
        const matchedBookmark = payload.available_bookmarks.find((item) => item.key === pendingBookmarkKey.current);
        setActionFeedback(`已切换到 ${matchedBookmark?.label ?? "当前阶段"}，现在可以开始讲这一步了。`);
        pendingBookmarkKey.current = null;
      }
      if (!didAutoPrepare.current) {
        didAutoPrepare.current = true;
        if (needsFirstTimeReset(payload)) {
          setActionFeedback("页面已自动准备到 08:00 初始态，第一次看建议从这里开始。");
          setActiveBookmarkKey(INITIAL_BOOKMARK_KEY);
          pendingBookmarkKey.current = INITIAL_BOOKMARK_KEY;
          void jumpToSimulationBookmark(INITIAL_BOOKMARK_KEY).catch(() => {
            pendingBookmarkKey.current = null;
            setActionFeedback("自动切回 08:00 失败了，你也可以手动点击“08:00 初始态”。");
          });
        } else {
          setActionFeedback("当前已经是最适合第一次观看的初始态，可以直接开始。");
        }
      }
    };

    void getSimulationState()
      .then((payload) => {
        applyWorldState(payload);
      })
      .catch(() => {
        if (isMounted) {
          setConnectionState("error");
        }
      });

    const socket = new WebSocket(websocketUrl());
    socket.onopen = () => setConnectionState("connected");
    socket.onclose = () => setConnectionState("disconnected");
    socket.onerror = () => setConnectionState("error");
    socket.onmessage = (event) => {
      applyWorldState(JSON.parse(event.data) as WorldState);
    };
    return () => {
      isMounted = false;
      socket.close();
    };
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
  const connectionStateLabel = useMemo(() => {
    if (connectionState === "connected") {
      return "已连接";
    }
    if (connectionState === "error") {
      return "连接错误";
    }
    if (connectionState === "disconnected") {
      return "已断开";
    }
    return "连接中";
  }, [connectionState]);
  const recommendedControlHint = useMemo(() => {
    if (!world || !demoPhase) {
      return "先等待页面拿到后端状态，然后从 08:00 开始。";
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

  const currentStepGuide = useMemo<StepGuide | null>(() => {
    if (!demoPhase) {
      return null;
    }
    if (demoPhase.label === "初始准备") {
      return {
        label: "08:00 初始态",
        observe: "先看只有 Alice 知道聚会；三个人分散在不同地点；每个人已经有自己的计划和位置。",
        proof: "这一步证明角色一开始就有不同的内部状态和计划，而不是随机同质地到处走。",
        operatorHint: "下一步直接点“10:00 第一次传播”，或者单步推进到 Alice 和 Bob 相遇。",
      };
    }
    if (demoPhase.label === "开始传播") {
      return {
        label: "10:00 第一次传播",
        observe: "重点看 Bob 是否刚获得信息、时间线是否出现传播事件、传播链是否新增 Alice -> Bob。",
        proof: "这一步证明一次局部对话会真实改写另一个角色的记忆和知识状态，而不只是显示一段文本。",
        operatorHint: "现在点击 Bob，去看他的最新话语、检索记忆和推理说明。",
      };
    }
    if (demoPhase.label === "传播完成") {
      return {
        label: "14:00 第二次传播",
        observe: "重点看 Carol 是否也知道聚会，以及传播链是否新增 Bob -> Carol。",
        proof: "这一步证明信息会沿着社交接触继续扩散，多个局部互动会累计成全局传播。",
        operatorHint: "再切到“14:30 反思形成态”，准备讲系统如何从多条记忆上升到高层反思。",
      };
    }
    return {
      label: "14:30 反思形成态",
      observe: "重点看反思数量是否变成 3、三位角色是否都已知道聚会，以及右侧是否出现高层总结语句。",
      proof: "这一步证明系统不只会存具体记忆，还会把多次互动总结成更高层的社会认知，也就是论文里的 reflection（高层反思）。",
      operatorHint: "现在点击任意角色，重点朗读它的反思文本和推理说明。",
    };
  }, [demoPhase]);

  const runAction = async (pendingMessage: string, action: () => Promise<void>, bookmarkKey?: string) => {
    setActionFeedback(pendingMessage);
    if (bookmarkKey) {
      pendingBookmarkKey.current = bookmarkKey;
      setActiveBookmarkKey(bookmarkKey);
      setSelectedAgentId(recommendedAgentIdForBookmark(bookmarkKey));
    }
    try {
      await action();
    } catch {
      pendingBookmarkKey.current = null;
      setActionFeedback("操作没有成功，请确认前后端仍然在运行。");
    }
  };

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
            这个课程演示版保留了论文里最关键的闭环：计划、记忆、对话、信息传播与反思。第一次使用时，不需要先理解所有细节，只要按时间书签一步一步看，就能看明白整条传播链。
          </p>
          <div className="story-strip">
            <span>先看 08:00：只有 Alice 知道聚会</span>
            <span>再看 10:00：Alice 把信息告诉 Bob</span>
            <span>最后看 14:30：系统形成共享反思</span>
          </div>
        </div>
        <div className="hero-actions panel control-panel">
          <div className="control-panel-header">
            <div>
              <p className="eyebrow">演示控制</p>
              <h2>控制小镇时间线</h2>
            </div>
            <span className={`status-pill ${connectionState}`}>{connectionStateLabel}</span>
          </div>
          <Controls
            running={world?.running ?? false}
            onStart={() => void runAction("开始自动演示中，出现关键事件后记得暂停。", () => postAction("/api/sim/start"))}
            onPause={() => void runAction("已暂停，适合现在开始讲解。", () => postAction("/api/sim/pause"))}
            onTick={() => void runAction("已请求单步推进，通常一秒内会看到状态更新。", () => postAction("/api/sim/tick"))}
            onReset={() =>
              void runAction("已重置到起点，建议先看 Alice 与 Bob 的第一次相遇。", () => postAction("/api/sim/reset"), INITIAL_BOOKMARK_KEY)
            }
            onSaveSnapshot={() => void runAction("正在保存当前快照，方便你稍后回到这个讲解节点。", () => saveSimulationSnapshot())}
            onLoadSnapshot={() => void runAction("正在恢复快照，页面会回到你之前保存的状态。", () => loadSimulationSnapshot())}
            onSetSpeed={(speedLabel) => void runAction(`已切换到 ${speedLabel}，如果讲解跟不上建议回到 1x 或使用单步推进。`, () => setSimulationSpeed(speedLabel))}
            onJumpToBookmark={(bookmarkKey) =>
              void runAction(
                `正在切换到 ${world?.available_bookmarks.find((item) => item.key === bookmarkKey)?.label ?? "指定阶段"}。`,
                () => jumpToSimulationBookmark(bookmarkKey),
                bookmarkKey,
              )
            }
            activeSpeedLabel={world?.active_speed_label ?? "1x"}
            availableSpeedLabels={world?.available_speed_labels ?? ["0.5x", "1x", "2x"]}
            availableBookmarks={world?.available_bookmarks ?? []}
            snapshotExists={world?.snapshot_status.exists ?? false}
            activeBookmarkKey={activeBookmarkKey}
            actionFeedback={actionFeedback}
            currentStepGuide={currentStepGuide}
          />
          <p className="control-note">
            建议先点 <strong>08:00 初始态</strong>，再点 <strong>10:00 第一次传播</strong>。如果你只想最快讲清楚，一开始不要直接点开始演示。
          </p>
        </div>
      </section>

      {world && demoPhase ? (
        <section className="guide-grid" aria-label="Presentation guidance">
          <article className="guide-card phase-card">
            <p className="summary-label">当前阶段</p>
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
            <p className="summary-label">现在建议怎么讲</p>
            <p className="guide-headline">{demoPhase.presenterCue}</p>
            <p className="guide-copy">{recommendedControlHint}</p>
            <div className="cue-footer">
              <span className="cue-kicker">下一步重点</span>
              <strong>{demoPhase.nextFocus}</strong>
            </div>
          </article>

          <article className="guide-card event-card">
            <p className="summary-label">最近发生的关键事件</p>
            {latestEvent ? (
              <>
                <div className="event-spotlight-topline">
                  <strong>{formatEventTitle(latestEvent.title)}</strong>
                  <span className={`event-type-pill spotlight ${latestEvent.event_type}`}>{formatEventTypeLabel(latestEvent.event_type)}</span>
                </div>
                <p className="guide-copy">{formatEventDetail(latestEvent.detail)}</p>
                <p className="micro-copy">
                  {latestEvent.time} · tick #{latestEvent.tick_count}
                </p>
              </>
            ) : (
              <p className="guide-copy">当前还没有新的关键事件。</p>
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
                ? `${formatLocationName(selectedLocation.name)} · ${formatPlanSummary(selectedAgent.active_plan?.summary ?? selectedAgent.current_action)}`
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
          <p>正在等待后端仿真状态。如果这里长时间不动，请先确认后端已经运行在 127.0.0.1:8000。</p>
        </section>
      )}
    </main>
  );
}
