import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  BookOpen,
  Calendar,
  Flame,
  Leaf,
  Recycle,
  Star,
  Target,
  Trophy,
  UserCircle,
  Zap,
} from "lucide-react";
import { educationApi } from "@/api/education";
import type { EcoFact } from "@/api/types";
import { ModeCard } from "@/components/quiz";
import { useAuthStore } from "@/stores/authStore";
import { useQuizStore } from "@/stores/quizStore";

const CATEGORY_COLORS: Record<string, string> = {
  FLORA: "bg-green-50 text-green-700 border-green-200",
  WATER: "bg-blue-50 text-blue-700 border-blue-200",
  WASTE: "bg-yellow-50 text-yellow-700 border-yellow-200",
  ENERGY: "bg-orange-50 text-orange-700 border-orange-200",
  FAUNA: "bg-purple-50 text-purple-700 border-purple-200",
};

export function MainMenu() {
  const { player, isAnonymous } = useAuthStore();
  const { playerStats, loadStats, dailyChallenge, loadDailyChallenge } = useQuizStore();
  const [dailyFact, setDailyFact] = useState<EcoFact | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    educationApi.getRandomFact().then(({ data }) => {
      if ("text_uz" in data) setDailyFact(data as EcoFact);
    });
    if (!isAnonymous) {
      loadStats();
      loadDailyChallenge();
    }
  }, [isAnonymous, loadStats, loadDailyChallenge]);

  const handleMode = (path: string, isProtected: boolean) => {
    if (isProtected && isAnonymous) {
      navigate("/login");
      return;
    }
    navigate(path);
  };

  return (
    <div className="flex flex-col gap-8">
      {/* Hero */}
      <div className="rounded-3xl bg-gradient-to-br from-green-800 to-emerald-600 p-8 flex flex-col gap-4">
        <div className="flex items-center gap-3">
          <Leaf size={32} className="text-green-200" />
          <h1 className="text-3xl font-bold text-white">EcoGame</h1>
        </div>
        <p className="text-green-100 text-base max-w-md">
          Ekologiya haqida bilimingizni sinab ko'ring. Savollar, streak va mukofotlar kutmoqda!
        </p>
        {playerStats && (
          <div className="flex items-center gap-4 mt-1 flex-wrap">
            <span className="bg-white/20 text-white text-xs font-semibold px-3 py-1 rounded-full">
              {playerStats.rank_title}
            </span>
            {playerStats.daily_streak > 0 && (
              <span className="flex items-center gap-1 bg-orange-400/30 text-white text-xs font-semibold px-3 py-1 rounded-full">
                <Flame size={12} />
                {playerStats.daily_streak} kun ketma-ket
              </span>
            )}
          </div>
        )}
      </div>

      {/* Player card */}
      {player && (
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 flex items-center gap-6 flex-wrap">
          <UserCircle size={36} className="text-green-600" />
          <div>
            <p className="text-xs text-gray-400">Profil</p>
            <p className="font-bold text-green-700">{player.nickname}</p>
            {isAnonymous && (
              <p className="text-xs text-gray-400 mt-0.5">
                Vaqtinchalik akkaunt —{" "}
                <button
                  onClick={() => navigate("/register")}
                  className="text-green-600 hover:underline font-medium"
                >
                  Ro'yxatdan o'ting
                </button>
              </p>
            )}
          </div>
          <div className="ml-auto flex items-center gap-4">
            {playerStats && (
              <>
                <div className="text-right">
                  <p className="text-xs text-gray-400">Aniqlik</p>
                  <p className="font-bold text-green-700">{Math.round(playerStats.accuracy_pct)}%</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-400">O'yinlar</p>
                  <p className="font-bold text-green-700">{playerStats.total_quizzes}</p>
                </div>
              </>
            )}
            <div className="flex items-center gap-2 text-gray-700">
              <Trophy size={18} className="text-yellow-500" />
              <span className="font-bold">{player.total_score}</span>
              <span className="text-xs text-gray-400">ball</span>
            </div>
          </div>
        </div>
      )}

      {/* Quiz modes */}
      <div>
        <h2 className="text-lg font-bold text-gray-700 mb-4">O'yin rejimlari</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <ModeCard
            title="Tezkor o'yin"
            description="10 ta tasodifiy savol"
            icon={<Zap size={24} className="text-yellow-500" />}
            color="bg-yellow-50"
            onClick={() => handleMode("/quiz/quick", true)}
          />
          <ModeCard
            title="Kunlik vazifa"
            description="Har kuni yangi savollar + bonus"
            icon={<Calendar size={24} className="text-blue-500" />}
            color="bg-blue-50"
            onClick={() => handleMode("/quiz/daily", true)}
            badge={dailyChallenge && !dailyChallenge.is_completed ? "Yangi!" : undefined}
          />
          <ModeCard
            title="Marafon"
            description="Birinchi xatogacha o'ynang"
            icon={<Flame size={24} className="text-red-500" />}
            color="bg-red-50"
            onClick={() => handleMode("/quiz/marathon", true)}
          />
          <ModeCard
            title="Kategoriya bo'yicha"
            description="Bir mavzudan chuqur savollar"
            icon={<Target size={24} className="text-purple-500" />}
            color="bg-purple-50"
            onClick={() => handleMode("/quiz/category/FLORA", true)}
          />
        </div>
      </div>

      {/* Mini game + Education row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <ModeCard
          title="Chiqindi saralash"
          description="Drag & drop mini-o'yin"
          icon={<Recycle size={24} className="text-green-600" />}
          color="bg-green-50"
          onClick={() => handleMode("/mini-game/sort", true)}
          badge="Mini"
        />
        <ModeCard
          title="O'qish"
          description="Ekologik maqolalar va faktlar"
          icon={<BookOpen size={24} className="text-teal-600" />}
          color="bg-teal-50"
          onClick={() => navigate("/education")}
        />
      </div>

      {/* Stats by category */}
      {playerStats && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Star size={16} className="text-yellow-500" />
            <h2 className="text-base font-bold text-gray-700">Kategoriya bo'yicha</h2>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
            {(Object.entries(playerStats.per_category) as [string, { total: number; correct: number; accuracy: number }][]).map(
              ([cat, stats]) => (
                <div
                  key={cat}
                  className={`rounded-xl p-3 border text-center cursor-pointer hover:shadow-md transition-shadow ${CATEGORY_COLORS[cat] ?? "bg-gray-50 border-gray-200"}`}
                  onClick={() => handleMode(`/quiz/category/${cat}`, true)}
                >
                  <p className="text-xs font-semibold">{cat}</p>
                  <p className="text-lg font-bold">{Math.round(stats.accuracy * 100)}%</p>
                  <p className="text-xs opacity-60">{stats.total} savol</p>
                </div>
              ),
            )}
          </div>
        </div>
      )}

      {/* Daily fact */}
      {dailyFact && (
        <div
          className={`rounded-2xl p-5 border ${CATEGORY_COLORS[dailyFact.category] ?? "bg-gray-50 text-gray-700 border-gray-200"}`}
        >
          <p className="text-xs font-semibold uppercase tracking-wide mb-1 opacity-60">
            Kunlik fakt
          </p>
          <p className="text-sm font-medium">{dailyFact.text_uz}</p>
          <p className="text-xs opacity-50 mt-1">— {dailyFact.source}</p>
        </div>
      )}
    </div>
  );
}
