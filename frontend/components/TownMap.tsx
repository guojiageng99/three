"use client";

import { Agent, Location } from "@/lib/types";
import { formatActionText, formatLocationDescription, formatLocationName } from "@/lib/presenter";

type TownMapProps = {
  agents: Agent[];
  locations: Location[];
  selectedAgentId: string | null;
  onSelectAgent: (agentId: string) => void;
  phaseLabel: string | null;
};

export function TownMap({ agents, locations, selectedAgentId, onSelectAgent, phaseLabel }: TownMapProps) {
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
          <p className="eyebrow">地图视图</p>
          <h2>小镇行为观测板</h2>
        </div>
        <p className="map-header-copy">
          地图展示当前各地点的角色分布。点击任意角色，可以在右侧查看其计划、记忆检索、推理和反思状态。
        </p>
      </div>
      <div className="map-guide-banner">
        <span className="map-guide-kicker">地图观看提示</span>
        <p>
          {phaseLabel === "初始准备"
            ? "先关注 Alice 和 Bob 的相遇，这是整段演示最自然的切入点。"
            : phaseLabel === "开始传播"
              ? "这一阶段重点不是移动本身，而是一次对话是否改变了角色知道的信息。"
              : phaseLabel === "传播完成"
                ? "此时地图要结合传播面板和时间线一起看，说明局部互动如何变成全局状态。"
                : phaseLabel === "反思形成"
                  ? "现在地图更多是在交代结果，讲解重心应转向右侧的反思与推理面板。"
                  : "先看角色所在位置，再把位置变化和右侧认知面板联系起来。"}
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
                <div className="location-name">{formatLocationName(location.name)}</div>
                <span className="occupancy-pill">{occupants.length} 人在此</span>
              </div>
              <div className="location-desc">{formatLocationDescription(location.description)}</div>
              <div className="agent-stack">
                {occupants.map((agent) => (
                  <button
                    key={agent.id}
                    className={selectedAgentId === agent.id ? "agent-chip selected" : "agent-chip"}
                    style={{ backgroundColor: agent.color }}
                    onClick={() => onSelectAgent(agent.id)}
                    title={formatActionText(agent.current_action)}
                    type="button"
                    aria-pressed={selectedAgentId === agent.id}
                  >
                    <span className="agent-chip-name">{agent.name}</span>
                    <span className="speech">{formatActionText(agent.current_action)}</span>
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
        <p>这个地图视图的目标不是复杂场景，而是方便课堂讲解和答辩录屏。</p>
      </div>
    </div>
  );
}
