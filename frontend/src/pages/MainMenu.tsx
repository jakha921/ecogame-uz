import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  BookOpen,
  Calendar,
  Flame,
  Leaf,
  Trophy,
  UserCircle,
  Zap,
} from "lucide-react";
import { educationApi } from "@/api/education";
import type { EcoFact } from "@/api/types";
import { useAuthStore } from "@/stores/authStore";

const CATEGORY_COLORS: Record<string, string> = {
  FLORA: "bg-green-50 text-green-700 border-green-200",
  WATER: "bg-blue-50 text-blue-700 border-blue-200",
  WASTE: "bg-yellow-50 text-yellow-700 border-yellow-200",
  ENERGY: "bg-orange-50 text-orange-700 border-orange-200",
  FAUNA: "bg-purple-50 text-purple-700 border-purple-200",
};

const QUIZ_MODES = [
  {
    key: "quick",
    path: "/quiz/quick",
    label: "Tezkor o'yin",
    description: "10 ta savol, barcha mavzular",
    icon: <Zap size={28} className="text-yellow-500" />,
    gradient: "from-yellow-500 to-orange-400",
    protected: true,
  },
  {
    key: "daily",
    path: "/quiz/daily",
    label: "Kunlik topshiriq",
    description: "Har kuni yangi savollar + bonus ball",
    icon: <Calendar size={28} className="text-blue-500" />,
    gradient: "from-blue-500 to-cyan-400",
    protected: true,
  },
  {
    key: "marathon",
    path: "/quiz/marathon",
    label: "Marafon",
    description: "Bitta xato = o'yin tugaydi",
    icon: <Flame size={28} className="text-red-500" />,
    gradient: "from-red-500 to-pink-400",
    protected: true,
  },
  {
    key: "education",
    path: "/education",
    label: "O'qish",
    description: "Ekologik maqolalar va faktlar",
    icon: <BookOpen size={28} className="text-green-600" />,
    gradient: "from-green-600 to-emerald-500",
    protected: false,
  },
];

export function MainMenu() {
  const { player, isAnonymous } = useAuthStore();
  const [dailyFact, setDailyFact] = useState<EcoFact | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    educationApi.getRandomFact().then(({ data }) => {
      if ("text_uz" in data) setDailyFact(data as EcoFact);
    });
  }, []);

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
          Ekologiya haqida bilimingizni sinab ko'ring. Savollar, darajalar va
          mukofotlar kutmoqda!
        </p>
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
          <div className="ml-auto flex items-center gap-2 text-gray-700">
            <Trophy size={18} className="text-yellow-500" />
            <span className="font-bold">{player.total_score}</span>
            <span className="text-xs text-gray-400">ball</span>
          </div>
        </div>
      )}

      {/* Quiz modes */}
      <div>
        <h2 className="text-lg font-bold text-gray-700 mb-4">O'yin rejimlari</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {QUIZ_MODES.map((mode) => (
            <button
              key={mode.key}
              onClick={() => handleMode(mode.path, mode.protected)}
              className="bg-white rounded-2xl border-2 border-transparent hover:border-green-400 hover:shadow-xl p-5 flex items-start gap-4 text-left transition-all cursor-pointer"
            >
              <div
                className={`rounded-xl p-3 bg-gradient-to-br ${mode.gradient} bg-opacity-10 flex-shrink-0`}
              >
                {mode.icon}
              </div>
              <div>
                <p className="font-bold text-gray-800">{mode.label}</p>
                <p className="text-sm text-gray-500 mt-0.5">{mode.description}</p>
              </div>
            </button>
          ))}
        </div>
      </div>

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
