"use client";

import { Agent, EventLog, KnowledgeEdge, RetrievalExplanation, SnapshotStatus } from "@/lib/types";

type SidebarProps = {
  agent: Agent | null;
  currentLocationName: string | null;
  events: EventLog[];
  knowledgeEdges: KnowledgeEdge[];
  knowledgeStatus: Record<string, string>;
  dayLabel: string;
  timeLabel: string;
  tickCount: number;
  llmEnabled: boolean;
  llmModel: string | null;
  activeSpeedLabel: string;
  snapshotStatus: SnapshotStatus;
  latestEvent: EventLog | null;
  phaseLabel: string | null;
  presenterCue: string | null;
  nextFocus: string | null;
};

export function Sidebar({
  agent,
  currentLocationName,
  events,
  knowledgeEdges,
  knowledgeStatus,
  dayLabel,
  timeLabel,
  tickCount,
  llmEnabled,
  llmModel,
  activeSpeedLabel,
  snapshotStatus,
  latestEvent,
  phaseLabel,
  presenterCue,
  nextFocus,
}: SidebarProps) {
  const explanationByMemoryId = new Map<string, RetrievalExplanation>(
    (agent?.retrieval_explanations ?? []).map((item) => [item.memory_id, item]),
  );

  return (
    <aside className="sidebar">
      <section className="panel status-panel">
        <div className="eyebrow">全局状态</div>
        <h2>{dayLabel}</h2>
        <p className="time-label">{timeLabel}</p>
        <div className="status-grid">
          <div>
            <span className="status-key">步数</span>
            <strong>#{tickCount}</strong>
          </div>
          <div>
            <span className="status-key">模式</span>
            <strong>{llmEnabled ? llmModel : "Fallback"}</strong>
          </div>
          <div>
            <span className="status-key">速度</span>
            <strong>{activeSpeedLabel}</strong>
          </div>
          <div>
            <span className="status-key">快照</span>
            <strong>{snapshotStatus.exists ? "已保存" : "暂无"}</strong>
          </div>
        </div>
        <p className="snapshot-copy">
          {snapshotStatus.exists
            ? `已保存到 ${snapshotStatus.label} · 第 ${snapshotStatus.tick_count} 步`
            : "当前还没有保存演示快照。"}
        </p>
      </section>

      <section className="panel agent-profile-panel">
        <div className="eyebrow">当前角色</div>
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
              <span className="callout-label">当前行为</span>
              <p>{agent.current_action}</p>
            </div>
            <div className="callout-card subtle">
              <span className="callout-label">最新话语</span>
              <p>{agent.last_utterance ?? "当前情境下暂无发言。"} </p>
            </div>
          </>
        ) : (
          <p>请先在地图上选择一个角色。</p>
        )}
      </section>

      <section className="panel highlight-panel">
        <div className="eyebrow">推理上下文</div>
        {agent ? (
          <>
            <div className="callout-card bright">
              <span className="callout-label">当前计划</span>
              <p>{agent.active_plan ? `${agent.active_plan.time_slot} ${agent.active_plan.summary}` : "当前没有激活计划"}</p>
            </div>
            <p className="reasoning-copy">{agent.reasoning_note ?? "当前状态下暂无显式推理说明。"}</p>
            {phaseLabel ? (
              <div className="callout-card phase-callout">
                <span className="callout-label">讲解重点</span>
                <p>{presenterCue ?? "可以结合这里的内容解释：当前记忆线索如何驱动角色行为。"}</p>
                {nextFocus ? <p className="micro-copy emphasis">{nextFocus}</p> : null}
              </div>
            ) : null}
          </>
        ) : (
          <p>尚未选择角色。</p>
        )}
      </section>

      <section className="panel spotlight-panel">
        <div className="eyebrow">当前时刻为何重要</div>
        {latestEvent ? (
          <>
            <div className="spotlight-header">
              <strong>{latestEvent.title}</strong>
              <span className={`event-type-pill spotlight ${latestEvent.event_type}`}>{latestEvent.event_type}</span>
            </div>
            <p className="guide-copy">{latestEvent.detail}</p>
            <p className="micro-copy">
              当前阶段：{phaseLabel ?? "未标注"} · {latestEvent.time}
            </p>
          </>
        ) : (
          <p>当前还没有高亮事件。</p>
        )}
      </section>

      <section className="panel">
        <div className="eyebrow">完整计划</div>
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
          <p>尚未选择角色。</p>
        )}
      </section>

      <section className="panel">
        <div className="eyebrow">检索到的记忆</div>
        {agent ? (
          <ul className="list timeline-list">
            {agent.retrieved_memories.length > 0 ? (
              agent.retrieved_memories.map((memory) => (
                <li key={memory.id} className="memory-explanation-row">
                  <strong>{memory.timestamp}</strong>
                  <div className="memory-explanation-body">
                    <span>{memory.text}</span>
                    <div className="tag-row">
                      {(explanationByMemoryId.get(memory.id)?.explanation_tags ?? ["explanation unavailable"]).map((tag) => (
                        <span className="mini-tag" key={`${memory.id}-${tag}`}>
                          {tag}
                        </span>
                      ))}
                    </div>
                    {explanationByMemoryId.get(memory.id) ? (
                      <p className="score-copy">
                        分数 {explanationByMemoryId.get(memory.id)?.total_score.toFixed(2)} · 关键词重叠{" "}
                        {explanationByMemoryId.get(memory.id)?.keyword_overlap_count}
                      </p>
                    ) : null}
                  </div>
                </li>
              ))
            ) : (
              <li>当前情境下没有检索到相关记忆。</li>
            )}
          </ul>
        ) : (
          <p>尚未选择角色。</p>
        )}
      </section>

      <section className="panel">
        <div className="eyebrow">近期记忆</div>
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
          <p>尚未选择角色。</p>
        )}
      </section>

      <section className="panel">
        <div className="eyebrow">反思结果</div>
        {agent ? (
          <ul className="list reflection-list">
            {agent.reflections.length > 0 ? (
              agent.reflections.map((memory) => <li key={memory.id}>{memory.text}</li>)
            ) : (
              <li>当前还没有反思生成。</li>
            )}
          </ul>
        ) : (
          <p>尚未选择角色。</p>
        )}
      </section>

      <section className="panel">
        <div className="eyebrow">信息传播</div>
        <ul className="list reflection-list">
          {Object.keys(knowledgeStatus).length > 0 ? (
            Object.entries(knowledgeStatus).map(([agentId, learnedAt]) => (
              <li key={agentId}>
                {agentId} 在 {learnedAt} 获得信息
              </li>
            ))
          ) : (
            <li>传播尚未发生。</li>
          )}
        </ul>
        <div className="spread-chain">
          {knowledgeEdges.length > 0 ? (
            knowledgeEdges.map((edge) => (
              <p key={`${edge.source_agent_id}-${edge.target_agent_id}-${edge.tick_count}`}>
                {edge.source_agent_id} -&gt; {edge.target_agent_id} · {edge.learned_at}
              </p>
            ))
          ) : (
            <p>当前还没有记录到传播链路。</p>
          )}
        </div>
        <p className="micro-copy">
          讲解时建议从上到下阅读这个面板，说明一次局部对话如何变成共享的全局事实。
        </p>
      </section>

      <section className="panel">
        <div className="eyebrow">事件时间线</div>
        <ul className="list timeline-list">
          {events.map((event) => (
            <li key={event.id} className={`event-row event-${event.event_type}`}>
              <strong>{event.time}</strong>
              <div className="timeline-body">
                <span className="event-type-pill">{event.event_type}</span>
                <span>
                  {event.title}: {event.detail}
                </span>
              </div>
            </li>
          ))}
        </ul>
      </section>
    </aside>
  );
}
