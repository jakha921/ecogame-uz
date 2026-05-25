import { useEffect, useState } from "react";
import {
  Bird,
  Crown,
  Droplets,
  Flame,
  Leaf,
  Recycle,
  Star,
  SunMedium,
  TreeDeciduous,
  Trophy,
  UserCircle,
  Wind,
} from "lucide-react";
import { quizApi } from "@/api/quiz";
import type { PlayerAchievement } from "@/api/types";
import { useAuthStore } from "@/stores/authStore";
import { t } from "@/i18n";

const ICON_MAP: Record<string, React.ReactNode> = {
  tree: <TreeDeciduous size={28} className="text-green-600" />,
  garden: <Leaf size={28} className="text-green-500" />,
  water: <Droplets size={28} className="text-blue-500" />,
  recycle: <Recycle size={28} className="text-yellow-600" />,
  star: <Star size={28} className="text-yellow-500" />,
  fire: <Flame size={28} className="text-orange-500" />,
  air: <Wind size={28} className="text-cyan-500" />,
  leaf: <Leaf size={28} className="text-green-400" />,
  solar: <SunMedium size={28} className="text-orange-400" />,
  crown: <Crown size={28} className="text-yellow-600" />,
  bird: <Bird size={28} className="text-purple-500" />,
  trophy: <Trophy size={28} className="text-yellow-500" />,
};

export function ProfilePage() {
  const { player, updateProfile } = useAuthStore();
  const [achievements, setAchievements] = useState<PlayerAchievement[]>([]);
  const [totalAchievements, setTotalAchievements] = useState(0);
  const [editing, setEditing] = useState(false);
  const [nickname, setNickname] = useState(player?.nickname ?? "");

  useEffect(() => {
    quizApi.getMyAchievements().then(({ data }) => setAchievements(data));
    quizApi.getAchievements().then(({ data }) => setTotalAchievements(data.count));
  }, []);

  const handleSave = async () => {
    await updateProfile({ nickname });
    setEditing(false);
  };

  if (!player) return null;

  return (
    <div className="max-w-2xl mx-auto flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-green-700">{t("profile.title")}</h1>

      {/* Player card */}
      <div className="bg-white rounded-2xl shadow-sm p-6 flex flex-col gap-4">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center">
            <UserCircle size={40} className="text-green-600" />
          </div>
          <div className="flex-1">
            {editing ? (
              <div className="flex gap-2">
                <input
                  value={nickname}
                  onChange={(e) => setNickname(e.target.value)}
                  className="border border-gray-300 rounded-lg px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
                />
                <button
                  onClick={handleSave}
                  className="bg-green-600 text-white text-sm px-3 py-1 rounded-lg"
                >
                  {t("profile.save")}
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold text-gray-800">{player.nickname}</h2>
                <button
                  onClick={() => setEditing(true)}
                  className="text-green-500 text-xs hover:underline"
                >
                  {t("profile.edit")}
                </button>
              </div>
            )}
            <p className="text-sm text-gray-400">@{player.username}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 pt-2 border-t">
          <div>
            <p className="text-xs text-gray-400">{t("profile.total_score")}</p>
            <p className="text-2xl font-bold text-green-700">{player.total_score}</p>
          </div>
          <div>
            <p className="text-xs text-gray-400">{t("profile.achievements")}</p>
            <p className="text-2xl font-bold text-green-700">
              {achievements.length}/{totalAchievements}
            </p>
          </div>
        </div>
      </div>

      {/* Achievements */}
      <div>
        <h2 className="text-lg font-bold text-gray-700 mb-3">{t("profile.achievements")}</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {achievements.map((pa) => (
            <div
              key={pa.id}
              className="bg-white rounded-xl p-4 border border-green-100 flex flex-col items-center text-center gap-2"
            >
              <span>
                {ICON_MAP[pa.achievement.icon] ?? (
                  <Trophy size={28} className="text-yellow-500" />
                )}
              </span>
              <p className="text-sm font-semibold text-gray-700">{pa.achievement.name_uz}</p>
              <p className="text-xs text-gray-400">{pa.achievement.description_uz}</p>
            </div>
          ))}
          {achievements.length === 0 && (
            <p className="text-gray-400 text-sm col-span-3 text-center py-4">
              Hali yutuq yo'q. O'ynashni boshlang!
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
