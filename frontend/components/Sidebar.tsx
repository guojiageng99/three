"use client";

import { Agent, EventLog, KnowledgeEdge, RetrievalExplanation, SnapshotStatus } from "@/lib/types";
import {
  formatActionText,
  formatAgentId,
  formatEventDetail,
  formatEventTitle,
  formatEventTypeLabel,
  formatExplanationTag,
  formatKnowledgeBadge,
  formatLocationName,
  formatModelMode,
  formatPlanSummary,
  formatRole,
  formatText,
} from "@/lib/presenter";

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
  const primaryReflection = agent?.reflections[0] ?? null;

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
            <strong>{formatModelMode(llmEnabled, llmModel)}</strong>
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
                <p className="agent-role">{formatRole(agent.role)}</p>
              </div>
            </div>
            <p className="agent-summary">{formatText(agent.profile_summary)}</p>
            <div className="fact-row">
              <span className="fact-pill">{formatLocationName(currentLocationName)}</span>
              <span className="fact-pill">{formatKnowledgeBadge(agent.knows_party)}</span>
            </div>
            <div className="callout-card">
              <span className="callout-label">当前行为</span>
              <p>{formatActionText(agent.current_action)}</p>
            </div>
            <div className="callout-card subtle">
              <span className="callout-label">最新话语</span>
              <p>{agent.last_utterance ? formatText(agent.last_utterance) : "当前情境下暂无发言。"} </p>
            </div>
          </>
        ) : (
          <p>请先在地图上选择一个角色。</p>
        )}
      </section>

      <section className="panel highlight-panel">
        <div className="eyebrow">此刻先看这三件事</div>
        {agent ? (
          <>
            <div className="callout-card bright">
              <span className="callout-label">当前计划</span>
              <p>{agent.active_plan ? `${agent.active_plan.time_slot} ${formatPlanSummary(agent.active_plan.summary)}` : "当前没有激活计划"}</p>
            </div>
            <div className="callout-card">
              <span className="callout-label">当前为什么这样行动</span>
              <p>{agent.reasoning_note ? formatText(agent.reasoning_note) : "当前状态下暂无显式推理说明。"}</p>
            </div>
            {phaseLabel ? (
              <div className="callout-card phase-callout">
                <span className="callout-label">此阶段重点</span>
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
              <strong>{formatEventTitle(latestEvent.title)}</strong>
              <span className={`event-type-pill spotlight ${latestEvent.event_type}`}>{formatEventTypeLabel(latestEvent.event_type)}</span>
            </div>
            <p className="guide-copy">{formatEventDetail(latestEvent.detail)}</p>
            <p className="micro-copy">
              当前阶段：{phaseLabel ?? "未标注"} · {latestEvent.time}
            </p>
          </>
        ) : (
          <p>当前还没有高亮事件。</p>
        )}
      </section>

      <section className="panel">
        <div className="eyebrow">传播与反思</div>
        {agent ? (
          <>
            <div className="callout-card">
              <span className="callout-label">角色是否知道聚会信息</span>
              <p>{agent.knows_party ? `${agent.name} 已经知道聚会信息。` : `${agent.name} 目前还不知道聚会信息。`}</p>
            </div>
            <div className="callout-card subtle">
              <span className="callout-label">当前最重要的反思</span>
              <p>{primaryReflection?.text ? formatText(primaryReflection.text) : "当前还没有形成高层反思，可以继续推进到 14:30 左右再看。"}</p>
            </div>
          </>
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
                {formatAgentId(agentId)} 在 {learnedAt} 获得信息
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
                {formatAgentId(edge.source_agent_id)} -&gt; {formatAgentId(edge.target_agent_id)} · {edge.learned_at}
              </p>
            ))
          ) : (
            <p>当前还没有记录到传播链路。</p>
          )}
        </div>
        <p className="micro-copy">这里最适合讲“局部对话如何一步步变成全局共享事实”。</p>
      </section>

      <details className="panel collapsible-panel" open={Boolean(agent?.reflections.length)}>
        <summary>展开认知细节（计划、记忆、时间线）</summary>
        <div className="details-stack">
          <section className="details-section">
            <div className="eyebrow">完整计划</div>
            {agent ? (
              <ul className="list timeline-list">
                {agent.plan.map((item) => (
                  <li
                    key={`${agent.id}-${item.time_slot}`}
                    className={agent.active_plan?.time_slot === item.time_slot ? "active-plan-row" : undefined}
                  >
                    <strong>{item.time_slot}</strong> {formatPlanSummary(item.summary)}
                  </li>
                ))}
              </ul>
            ) : (
              <p>尚未选择角色。</p>
            )}
          </section>

          <section className="details-section">
            <div className="eyebrow">检索到的记忆</div>
            {agent ? (
              <ul className="list timeline-list">
                {agent.retrieved_memories.length > 0 ? (
                  agent.retrieved_memories.map((memory) => (
                    <li key={memory.id} className="memory-explanation-row">
                      <strong>{memory.timestamp}</strong>
                      <div className="memory-explanation-body">
                        <span>{formatText(memory.text)}</span>
                        <div className="tag-row">
                          {(explanationByMemoryId.get(memory.id)?.explanation_tags ?? ["explanation unavailable"]).map((tag) => (
                            <span className="mini-tag" key={`${memory.id}-${tag}`}>
                              {formatExplanationTag(tag)}
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

          <section className="details-section">
            <div className="eyebrow">近期记忆</div>
            {agent ? (
              <ul className="list timeline-list">
                {agent.recent_memories.map((memory) => (
                  <li key={memory.id}>
                    <strong>{memory.timestamp}</strong>
                    <span>{formatText(memory.text)}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p>尚未选择角色。</p>
            )}
          </section>

          <section className="details-section">
            <div className="eyebrow">事件时间线</div>
            <ul className="list timeline-list">
              {events.map((event) => (
                <li key={event.id} className={`event-row event-${event.event_type}`}>
                  <strong>{event.time}</strong>
                  <div className="timeline-body">
                    <span className="event-type-pill">{formatEventTypeLabel(event.event_type)}</span>
                    <span>
                      {formatEventTitle(event.title)}: {formatEventDetail(event.detail)}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          </section>
        </div>
      </details>
    </aside>
  );
}
