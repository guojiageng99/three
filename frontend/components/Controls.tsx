"use client";

type ControlsProps = {
  onStart: () => void;
  onPause: () => void;
  onTick: () => void;
  onReset: () => void;
  onSaveSnapshot: () => void;
  onLoadSnapshot: () => void;
  onSetSpeed: (speedLabel: string) => void;
  running: boolean;
  activeSpeedLabel: string;
  availableSpeedLabels: string[];
  snapshotExists: boolean;
};

export function Controls({
  onStart,
  onPause,
  onTick,
  onReset,
  onSaveSnapshot,
  onLoadSnapshot,
  onSetSpeed,
  running,
  activeSpeedLabel,
  availableSpeedLabels,
  snapshotExists,
}: ControlsProps) {
  return (
    <div className="control-stack">
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
    </div>
  );
}
