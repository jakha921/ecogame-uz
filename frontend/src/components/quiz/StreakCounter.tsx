import { Flame } from "lucide-react";

interface StreakCounterProps {
  streak: number;
  multiplier: number;
}

export function StreakCounter({ streak, multiplier }: StreakCounterProps) {
  if (streak < 2) return null;

  return (
    <div className="flex items-center gap-2 bg-orange-50 border border-orange-200 rounded-xl px-4 py-2 self-start">
      <Flame size={20} className="text-orange-500" />
      <span className="text-sm font-bold text-orange-700">
        {streak} ketma-ket!
      </span>
      <span className="text-xs font-semibold text-orange-500 bg-orange-100 rounded-full px-2 py-0.5">
        ×{multiplier.toFixed(1)}
      </span>
    </div>
  );
}
