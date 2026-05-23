import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { educationApi } from "@/api/education";
import type { EcoFact, Level } from "@/api/types";
import { useAuthStore } from "@/stores/authStore";
import { useGameStore } from "@/stores/gameStore";
import { t } from "@/i18n";

const CATEGORY_COLORS: Record<string, string> = {
  FLORA: "bg-green-100 text-green-700",
  WATER: "bg-blue-100 text-blue-700",
  WASTE: "bg-yellow-100 text-yellow-700",
  ENERGY: "bg-orange-100 text-orange-700",
  FAUNA: "bg-purple-100 text-purple-700",
};

function LevelCard({ level, onPlay }: { level: Level; onPlay: (id: number) => void }) {
  const locked = !level.is_unlocked;

  return (
    <div
      className={`rounded-2xl border-2 p-6 flex flex-col gap-3 transition-all ${
        locked
          ? "bg-gray-50 border-gray-200 opacity-60"
          : "bg-white border-green-200 hover:border-green-400 hover:shadow-md cursor-pointer"
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
          {t("game.level")} {level.number}
        </span>
        {locked && <span className="text-lg">🔒</span>}
        {!locked && level.is_unlocked && <span className="text-green-500 text-sm">✓</span>}
      </div>

      <h2 className="text-lg font-bold text-gray-800">{level.name_uz}</h2>
      <p className="text-sm text-gray-500 line-clamp-2">{level.description_uz}</p>

      {locked && (
        <p className="text-xs text-gray-400">
          {t("game.required_score")}: {level.required_score} ball
        </p>
      )}

      {!locked && (
        <button
          onClick={() => onPlay(level.id)}
          className="mt-auto bg-green-600 hover:bg-green-500 text-white text-sm font-semibold py-2 rounded-lg transition-colors"
        >
          {t("game.start")}
        </button>
      )}
    </div>
  );
}

export function MainMenu() {
  const { levels, loadLevels, isLoading } = useGameStore();
  const { player, isAuthenticated } = useAuthStore();
  const [dailyFact, setDailyFact] = useState<EcoFact | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadLevels();
    educationApi.getRandomFact().then(({ data }) => {
      if ("text_uz" in data) setDailyFact(data as EcoFact);
    });
  }, [loadLevels]);

  const handlePlay = (levelId: number) => {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }
    navigate(`/play/${levelId}`);
  };

  return (
    <div className="flex flex-col gap-8">
      {/* Hero */}
      <div className="text-center py-8">
        <h1 className="text-4xl font-bold text-green-700 mb-2">🌿 EcoGame</h1>
        <p className="text-gray-600 text-lg">Ekologiyani o'yin orqali o'rgan va muhofaza qil!</p>
      </div>

      {/* Player stats */}
      {player && (
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-green-100 flex gap-6 flex-wrap">
          <div>
            <p className="text-xs text-gray-400">{t("menu.profile")}</p>
            <p className="font-bold text-green-700">{player.nickname}</p>
          </div>
          <div>
            <p className="text-xs text-gray-400">{t("profile.total_score")}</p>
            <p className="font-bold text-gray-800">{player.total_score} ball</p>
          </div>
        </div>
      )}

      {/* Daily fact */}
      {dailyFact && (
        <div
          className={`rounded-2xl p-5 ${CATEGORY_COLORS[dailyFact.category] ?? "bg-gray-100 text-gray-700"}`}
        >
          <p className="text-xs font-semibold uppercase mb-1">{t("education.daily_fact")}</p>
          <p className="text-sm font-medium">{dailyFact.text_uz}</p>
          <p className="text-xs opacity-60 mt-1">— {dailyFact.source}</p>
        </div>
      )}

      {/* Levels grid */}
      <div>
        <h2 className="text-xl font-bold text-gray-700 mb-4">Darajalar</h2>
        {isLoading ? (
          <p className="text-gray-400 text-center py-8">Yuklanmoqda...</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {levels.map((level: Level) => (
              <LevelCard key={level.id} level={level} onPlay={handlePlay} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
