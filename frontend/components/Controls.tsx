"use client";

import { DemoBookmark } from "@/lib/types";

type ControlsProps = {
  onStart: () => void;
  onPause: () => void;
  onTick: () => void;
  onReset: () => void;
  onSaveSnapshot: () => void;
  onLoadSnapshot: () => void;
  onSetSpeed: (speedLabel: string) => void;
  onJumpToBookmark: (bookmarkKey: string) => void;
  running: boolean;
  activeSpeedLabel: string;
  availableSpeedLabels: string[];
  availableBookmarks: DemoBookmark[];
  snapshotExists: boolean;
  activeBookmarkKey: string | null;
  actionFeedback: string | null;
  currentStepGuide: {
    label: string;
    observe: string;
    proof: string;
    operatorHint: string;
  } | null;
};

export function Controls({
  onStart,
  onPause,
  onTick,
  onReset,
  onSaveSnapshot,
  onLoadSnapshot,
  onSetSpeed,
  onJumpToBookmark,
  running,
  activeSpeedLabel,
  availableSpeedLabels,
  availableBookmarks,
  snapshotExists,
  activeBookmarkKey,
  actionFeedback,
  currentStepGuide,
}: ControlsProps) {
  return (
    <div className="control-stack">
      <div className="quick-start-guide">
        <div className="quick-start-header">
          <p className="eyebrow">第一次看先这样操作</p>
          <h3>先按这 3 步走</h3>
        </div>
        <ol className="quick-start-list">
          <li>
            <span className="step-index">1</span>
            <div>
              <strong>点 `08:00 初始态`</strong>
              <p>先从只有 Alice 知道聚会的起点开始，不要直接看结局。</p>
            </div>
          </li>
          <li>
            <span className="step-index">2</span>
            <div>
              <strong>点 `10:00 第一次传播`</strong>
              <p>看 Alice 把信息告诉 Bob，理解“对话会改变角色状态”。</p>
            </div>
          </li>
          <li>
            <span className="step-index">3</span>
            <div>
              <strong>再看 `14:00` 和 `14:30`</strong>
              <p>观察 Bob 如何继续传播，以及系统何时形成高层反思。</p>
            </div>
          </li>
        </ol>
      </div>
      {currentStepGuide ? (
        <div className="proof-guide">
          <div className="quick-start-header">
            <p className="eyebrow">当前书签说明</p>
            <h3>{currentStepGuide.label}</h3>
          </div>
          <div className="proof-guide-grid">
            <div>
              <strong>现在先看什么</strong>
              <p>{currentStepGuide.observe}</p>
            </div>
            <div>
              <strong>这一步说明什么</strong>
              <p>{currentStepGuide.proof}</p>
            </div>
            <div>
              <strong>接下来怎么点</strong>
              <p>{currentStepGuide.operatorHint}</p>
            </div>
          </div>
        </div>
      ) : null}
      <div className="controls">
        <button type="button" className="primary" onClick={running ? onPause : onStart}>
          {running ? "暂停演示" : "开始演示"}
        </button>
        <button type="button" onClick={onTick}>
          单步推进
        </button>
        <button type="button" onClick={onReset}>
          重置场景
        </button>
        <button type="button" onClick={onSaveSnapshot}>
          保存快照
        </button>
        <button type="button" onClick={onLoadSnapshot} disabled={!snapshotExists}>
          恢复快照
        </button>
      </div>
      <div className="speed-group" aria-label="Simulation speed controls">
        {availableSpeedLabels.map((speedLabel) => (
          <button
            key={speedLabel}
            type="button"
            className={speedLabel === activeSpeedLabel ? "speed-chip active" : "speed-chip"}
            onClick={() => onSetSpeed(speedLabel)}
          >
            {speedLabel}
          </button>
        ))}
      </div>
      <div className="bookmark-group" aria-label="Demo bookmark controls">
        {availableBookmarks.map((bookmark) => (
          <button
            key={bookmark.key}
            type="button"
            className={bookmark.key === activeBookmarkKey ? "bookmark-chip active" : "bookmark-chip"}
            onClick={() => onJumpToBookmark(bookmark.key)}
            title={bookmark.description}
          >
            {bookmark.label}
          </button>
        ))}
      </div>
      {actionFeedback ? <p className="action-feedback">{actionFeedback}</p> : null}
    </div>
  );
}
