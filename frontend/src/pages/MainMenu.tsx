import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Grid2x2,
  Leaf,
  Lock,
  MapPin,
  MousePointerClick,
  PlayCircle,
  Recycle,
  Sprout,
  Star,
  Target,
  Trophy,
  UserCircle,
} from "lucide-react";
import { educationApi } from "@/api/education";
import type { EcoFact, Level } from "@/api/types";
import { useAuthStore } from "@/stores/authStore";
import { useGameStore } from "@/stores/gameStore";
import { t } from "@/i18n";

// Tashkent location tags matching the new level names
const LEVEL_LOCATION: Record<number, string> = {
  1: "Toshkent",
  2: "Chorsu",
  3: "Shahar markazi",
  4: "Chirchiq",
};

const LEVEL_GRADIENT: Record<number, string> = {
  1: "from-green-700 to-green-500",
  2: "from-teal-700 to-teal-500",
  3: "from-blue-700 to-blue-500",
  4: "from-cyan-700 to-cyan-500",
};

const CATEGORY_COLORS: Record<string, string> = {
  FLORA: "bg-green-50 text-green-700 border-green-200",
  WATER: "bg-blue-50 text-blue-700 border-blue-200",
  WASTE: "bg-yellow-50 text-yellow-700 border-yellow-200",
  ENERGY: "bg-orange-50 text-orange-700 border-orange-200",
  FAUNA: "bg-purple-50 text-purple-700 border-purple-200",
};

function LevelCard({ level, onPlay }: { level: Level; onPlay: (id: number) => void }) {
  const locked = !level.is_unlocked;
  const mc = level.map_config as { iso_width?: number; iso_height?: number };
  const gridSize = mc.iso_width && mc.iso_height ? `${mc.iso_width}×${mc.iso_height}` : null;
  const gradient = LEVEL_GRADIENT[level.number] ?? "from-gray-700 to-gray-500";
  const location = LEVEL_LOCATION[level.number] ?? "";

  return (
    <div
      className={[
        "rounded-2xl overflow-hidden border-2 flex flex-col transition-all",
        locked
          ? "border-gray-200 opacity-60 cursor-default"
          : "border-transparent hover:border-green-400 hover:shadow-xl cursor-pointer",
      ].join(" ")}
      onClick={locked ? undefined : () => onPlay(level.id)}
    >
      {/* Gradient header */}
      <div className={`bg-gradient-to-br ${gradient} p-5 flex flex-col gap-1`}>
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-white/70 uppercase tracking-widest">
            {t("game.level")} {level.number}
          </span>
          {locked ? (
            <Lock size={14} className="text-white/60" />
          ) : (
            <MapPin size={14} className="text-white/70" />
          )}
        </div>
        <h2 className="text-lg font-bold text-white">{level.name_uz}</h2>
        {location && (
          <p className="text-xs text-white/60 flex items-center gap-1">
            <MapPin size={10} />
            {location}
          </p>
        )}
      </div>

      {/* Body */}
      <div className="bg-white p-4 flex flex-col gap-3 flex-1">
        <p className="text-sm text-gray-500 line-clamp-2">{level.description_uz}</p>

        <div className="flex items-center gap-3 text-xs text-gray-400">
          {gridSize && (
            <span className="flex items-center gap-1">
              <Grid2x2 size={11} />
              {gridSize} xarita
            </span>
          )}
          {level.required_score > 0 && (
            <span className="flex items-center gap-1">
              <Star size={11} />
              {level.required_score} ball kerak
            </span>
          )}
        </div>

        {locked ? (
          <div className="mt-auto flex items-center gap-2 text-xs text-gray-400 border border-gray-200 rounded-lg px-3 py-2">
            <Lock size={12} />
            {level.required_score} ball to'plang
          </div>
        ) : (
          <button className="mt-auto bg-green-600 hover:bg-green-500 text-white text-sm font-semibold py-2 rounded-xl transition-colors flex items-center justify-center gap-2">
            <PlayCircle size={16} />
            {t("game.start")}
          </button>
        )}
      </div>
    </div>
  );
}

export function MainMenu() {
  const { levels, loadLevels, isLoading } = useGameStore();
  const { player, isAnonymous } = useAuthStore();
  const [dailyFact, setDailyFact] = useState<EcoFact | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadLevels();
    educationApi.getRandomFact().then(({ data }) => {
      if ("text_uz" in data) setDailyFact(data as EcoFact);
    });
  }, [loadLevels]);

  const handlePlay = (levelId: number) => {
    navigate(`/play/${levelId}`);
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
          Toshkent shahrini ekologik tiklang. Daraxt o'tqazing, suv tozalang, hayvonlarni himoya qiling.
        </p>
        {/* How to play — 4 steps */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-2">
          {[
            { icon: <MousePointerClick size={18} />, text: "Pastdan qurol tanlang" },
            { icon: <Sprout size={18} />, text: "Xaritaga bosib joylang" },
            { icon: <Recycle size={18} />, text: "Ob'ektlar o'sib atrofni yaxshilaydi" },
            { icon: <Target size={18} />, text: "4 ko'rsatkichni 80% ga yetkazing" },
          ].map(({ icon, text }, i) => (
            <div key={i} className="bg-white/10 rounded-xl p-3 flex flex-col items-center gap-2 text-center">
              <span className="text-green-200">{icon}</span>
              <p className="text-xs text-green-100 leading-tight">{text}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Player stats */}
      {player && (
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 flex items-center gap-6 flex-wrap">
          <UserCircle size={36} className="text-green-600" />
          <div>
            <p className="text-xs text-gray-400">{t("menu.profile")}</p>
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
          <div className="ml-auto flex items-center gap-2 text-gray-700">
            <Trophy size={18} className="text-yellow-500" />
            <span className="font-bold">{player.total_score}</span>
            <span className="text-xs text-gray-400">ball</span>
          </div>
        </div>
      )}

      {/* Daily fact */}
      {dailyFact && (
        <div
          className={`rounded-2xl p-5 border ${CATEGORY_COLORS[dailyFact.category] ?? "bg-gray-50 text-gray-700 border-gray-200"}`}
        >
          <p className="text-xs font-semibold uppercase tracking-wide mb-1 opacity-60">
            {t("education.daily_fact")}
          </p>
          <p className="text-sm font-medium">{dailyFact.text_uz}</p>
          <p className="text-xs opacity-50 mt-1">— {dailyFact.source}</p>
        </div>
      )}

      {/* Levels grid */}
      <div>
        <h2 className="text-lg font-bold text-gray-700 mb-4">Darajalar — Toshkent lokatsiyalari</h2>
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
