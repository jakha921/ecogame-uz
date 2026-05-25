import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Award, Flame, Home, RotateCcw, Target, Trophy } from "lucide-react";
import { useQuizStore } from "@/stores/quizStore";

export function QuizResultsPage() {
  const navigate = useNavigate();
  const { quizResult, reset } = useQuizStore();

  useEffect(() => {
    if (!quizResult) {
      navigate("/");
    }
  }, [quizResult, navigate]);

  if (!quizResult) return null;

  const { session, accuracy, rank_title, achievements_unlocked } = quizResult;

  const handlePlayAgain = () => {
    reset();
    navigate("/quiz/quick");
  };

  const handleHome = () => {
    reset();
    navigate("/");
  };

  return (
    <div className="max-w-lg mx-auto flex flex-col gap-6 animate-in fade-in duration-500">
      {/* Score card */}
      <div className="bg-gradient-to-br from-green-700 to-emerald-500 rounded-3xl p-8 text-center text-white flex flex-col gap-3">
        <p className="text-green-100 text-sm font-semibold uppercase tracking-widest">
          Sizning natijangiz
        </p>
        <p className="text-6xl font-bold">{session.score}</p>
        <p className="text-green-200 text-sm">ball</p>
        <div className="mt-2 bg-white/20 rounded-xl px-4 py-2 inline-block self-center">
          <p className="text-white font-semibold">{rank_title}</p>
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-white rounded-2xl p-4 text-center border border-gray-100 shadow-sm">
          <Target size={20} className="text-green-600 mx-auto mb-1" />
          <p className="text-xl font-bold text-gray-800">
            {Math.round(accuracy * 100)}%
          </p>
          <p className="text-xs text-gray-400">Aniqlik</p>
        </div>
        <div className="bg-white rounded-2xl p-4 text-center border border-gray-100 shadow-sm">
          <Flame size={20} className="text-orange-500 mx-auto mb-1" />
          <p className="text-xl font-bold text-gray-800">{session.max_streak}</p>
          <p className="text-xs text-gray-400">Eng uzun</p>
        </div>
        <div className="bg-white rounded-2xl p-4 text-center border border-gray-100 shadow-sm">
          <Trophy size={20} className="text-yellow-500 mx-auto mb-1" />
          <p className="text-xl font-bold text-gray-800">
            {session.correct_count}/{session.total_questions}
          </p>
          <p className="text-xs text-gray-400">To'g'ri</p>
        </div>
      </div>

      {/* Achievements */}
      {achievements_unlocked.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-2xl p-5 flex flex-col gap-3">
          <div className="flex items-center gap-2">
            <Award size={20} className="text-yellow-600" />
            <p className="font-bold text-yellow-800">Yangi yutuqlar!</p>
          </div>
          <div className="flex flex-col gap-2">
            {achievements_unlocked.map((a) => (
              <div key={a.id} className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-yellow-200 flex items-center justify-center text-sm">
                  {a.icon}
                </div>
                <div>
                  <p className="text-sm font-semibold text-yellow-900">{a.name_uz}</p>
                  <p className="text-xs text-yellow-700">{a.description_uz}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        <button
          onClick={handlePlayAgain}
          className="flex-1 bg-green-600 hover:bg-green-500 text-white font-semibold py-3 rounded-2xl transition-colors flex items-center justify-center gap-2"
        >
          <RotateCcw size={18} />
          Yana o'ynash
        </button>
        <button
          onClick={handleHome}
          className="flex-1 bg-white border-2 border-gray-200 hover:border-green-400 text-gray-700 font-semibold py-3 rounded-2xl transition-colors flex items-center justify-center gap-2"
        >
          <Home size={18} />
          Bosh menyu
        </button>
      </div>
    </div>
  );
}
