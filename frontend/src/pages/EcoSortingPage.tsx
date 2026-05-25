import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Home, Loader2, RotateCcw, Trophy } from "lucide-react";
import { quizApi } from "@/api/quiz";
import { SortingGame } from "@/components/mini-game/SortingGame";
import { SORTING_ITEMS } from "@/data/sortingItems";

type PagePhase = "playing" | "submitting" | "done";

interface GameResult {
  score: number;
  correctCount: number;
  totalItems: number;
}

export function EcoSortingPage() {
  const navigate = useNavigate();
  const [phase, setPhase] = useState<PagePhase>("playing");
  const [result, setResult] = useState<GameResult | null>(null);
  const [gameKey, setGameKey] = useState(0);

  const handleComplete = useCallback(
    async (score: number, correctCount: number, totalItems: number) => {
      setPhase("submitting");
      try {
        await quizApi.submitMiniGameScore({ score, correct_count: correctCount, total_items: totalItems });
      } catch {
        // Score submission failure is non-critical
      }
      setResult({ score, correctCount, totalItems });
      setPhase("done");
    },
    [],
  );

  const handlePlayAgain = () => {
    setResult(null);
    setPhase("playing");
    setGameKey((k) => k + 1);
  };

  return (
    <div className="max-w-lg mx-auto flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-green-700">Chiqindi saralash</h1>
        <span className="text-sm text-gray-400">{SORTING_ITEMS.length} predmet</span>
      </div>

      {phase === "submitting" && (
        <div className="flex items-center justify-center py-12">
          <Loader2 size={32} className="animate-spin text-green-600" />
        </div>
      )}

      {phase === "playing" && (
        <SortingGame key={gameKey} onComplete={handleComplete} />
      )}

      {phase === "done" && result && (
        <div className="flex flex-col gap-6 animate-in fade-in duration-500">
          {/* Result card */}
          <div className="bg-gradient-to-br from-green-700 to-emerald-500 rounded-3xl p-8 text-center text-white flex flex-col gap-3">
            <Trophy size={40} className="mx-auto text-yellow-300" />
            <p className="text-green-100 text-sm font-semibold uppercase tracking-widest">
              Natija
            </p>
            <p className="text-6xl font-bold">{result.score}</p>
            <p className="text-green-200 text-sm">ball</p>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="bg-white rounded-2xl p-4 text-center border border-gray-100 shadow-sm">
              <p className="text-2xl font-bold text-gray-800">
                {result.correctCount}/{result.totalItems}
              </p>
              <p className="text-xs text-gray-400 mt-1">To'g'ri saralangan</p>
            </div>
            <div className="bg-white rounded-2xl p-4 text-center border border-gray-100 shadow-sm">
              <p className="text-2xl font-bold text-gray-800">
                {Math.round((result.correctCount / result.totalItems) * 100)}%
              </p>
              <p className="text-xs text-gray-400 mt-1">Aniqlik</p>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={handlePlayAgain}
              className="flex-1 bg-green-600 hover:bg-green-500 text-white font-semibold py-3 rounded-2xl transition-colors flex items-center justify-center gap-2"
            >
              <RotateCcw size={18} />
              Yana o'ynash
            </button>
            <button
              onClick={() => navigate("/")}
              className="flex-1 bg-white border-2 border-gray-200 hover:border-green-400 text-gray-700 font-semibold py-3 rounded-2xl transition-colors flex items-center justify-center gap-2"
            >
              <Home size={18} />
              Bosh menyu
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
