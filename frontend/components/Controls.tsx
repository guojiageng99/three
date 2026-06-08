"use client";

type ControlsProps = {
  onStart: () => void;
  onPause: () => void;
  onTick: () => void;
  onReset: () => void;
  running: boolean;
};

export function Controls({ onStart, onPause, onTick, onReset, running }: ControlsProps) {
  return (
    <div className="controls">
      <button type="button" className="primary" onClick={running ? onPause : onStart}>
        {running ? "Pause" : "Start"}
      </button>
      <button type="button" onClick={onTick}>
        Single Tick
      </button>
      <button type="button" onClick={onReset}>
        Reset
      </button>
    </div>
  );
}
