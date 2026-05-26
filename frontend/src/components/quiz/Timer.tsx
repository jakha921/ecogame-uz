import { useEffect, useRef, useState } from "react";

interface TimerProps {
  timeLimit: number;
  onTimeUp: () => void;
  active: boolean;
}

const RADIUS = 20;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

export function Timer({ timeLimit, onTimeUp, active }: TimerProps) {
  const [elapsed, setElapsed] = useState(0);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setElapsed(0);
    if (!active) return;

    intervalRef.current = setInterval(() => {
      setElapsed((prev) => {
        const next = prev + 100;
        if (next >= timeLimit * 1000) {
          clearInterval(intervalRef.current!);
          onTimeUp();
          return timeLimit * 1000;
        }
        return next;
      });
    }, 100);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [active, timeLimit, onTimeUp]);

  const ratio = Math.max(0, 1 - elapsed / (timeLimit * 1000));
  const remaining = Math.ceil((timeLimit * 1000 - elapsed) / 1000);
  const offset = CIRCUMFERENCE * (1 - ratio);

  const color = ratio > 0.5 ? "#22c55e" : ratio > 0.2 ? "#eab308" : "#ef4444";

  return (
    <div className="relative flex items-center justify-center w-14 h-14">
      <svg width="56" height="56" viewBox="0 0 56 56" className="-rotate-90">
        <circle cx="28" cy="28" r={RADIUS} fill="none" stroke="#e5e7eb" strokeWidth="4" />
        <circle
          cx="28"
          cy="28"
          r={RADIUS}
          fill="none"
          stroke={color}
          strokeWidth="4"
          strokeDasharray={CIRCUMFERENCE}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 0.1s linear, stroke 0.3s" }}
        />
      </svg>
      <span
        className="absolute text-sm font-bold"
        style={{ color }}
      >
        {remaining}
      </span>
    </div>
  );
}
