import { Flame, Star } from "lucide-react";

interface QuizHeaderProps {
  current: number;
  total: number;
  score: number;
  streak: number;
  streakMultiplier: number;
}

export function QuizHeader({ current, total, score, streak, streakMultiplier }: QuizHeaderProps) {
  const progress = total > 0 ? (current / total) * 100 : 0;

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-gray-600">
          Savol {current} / {total}
        </span>
        <div className="flex items-center gap-3">
          {streak >= 2 && (
            <span className="flex items-center gap-1 text-orange-500 font-semibold text-xs bg-orange-50 px-2 py-0.5 rounded-full">
              <Flame size={12} />
              ×{streakMultiplier.toFixed(1)}
            </span>
          )}
          <span className="flex items-center gap-1 text-green-700 font-bold">
            <Star size={14} className="text-yellow-500" />
            {score}
          </span>
        </div>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-green-500 h-2 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
}
