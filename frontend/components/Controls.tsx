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
  isActionPending: boolean;
  currentStepGuide: {
    label: string;
    focusAgent: string;
    focusReason: string;
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
  isActionPending,
}: ControlsProps) {
  return (
    <div className="control-stack">
      <div className="controls">
        <button type="button" className="primary" onClick={running ? onPause : onStart} disabled={isActionPending}>
          {running ? "暂停演示" : "开始演示"}
        </button>
        <button type="button" className="primary secondary-action" onClick={onTick} disabled={isActionPending}>
          {isActionPending ? "推进中…" : "单步推进"}
        </button>
        <button type="button" onClick={onReset} disabled={isActionPending}>
          重置场景
        </button>
        <button type="button" onClick={onSaveSnapshot} disabled={isActionPending}>
          保存快照
        </button>
        <button type="button" onClick={onLoadSnapshot} disabled={isActionPending || !snapshotExists}>
          恢复快照
        </button>
      </div>
      <div className="bookmark-group" aria-label="Demo bookmark controls">
        {availableBookmarks.map((bookmark) => (
          <button
            key={bookmark.key}
            type="button"
            className={bookmark.key === activeBookmarkKey ? "bookmark-chip active" : "bookmark-chip"}
            onClick={() => onJumpToBookmark(bookmark.key)}
            title={bookmark.description}
            disabled={isActionPending}
          >
            {bookmark.label}
          </button>
        ))}
      </div>
      <div className="speed-group" aria-label="Simulation speed controls">
        {availableSpeedLabels.map((speedLabel) => (
          <button
            key={speedLabel}
            type="button"
            className={speedLabel === activeSpeedLabel ? "speed-chip active" : "speed-chip"}
            onClick={() => onSetSpeed(speedLabel)}
            disabled={isActionPending}
          >
            {speedLabel}
          </button>
        ))}
      </div>
      {actionFeedback ? <p className="action-feedback">{actionFeedback}</p> : null}
    </div>
  );
}
