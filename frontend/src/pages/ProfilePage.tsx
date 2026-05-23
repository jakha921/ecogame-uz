import { useEffect, useState } from "react";
import { gameApi } from "@/api/game";
import type { PlayerAchievement } from "@/api/types";
import { useAuthStore } from "@/stores/authStore";
import { t } from "@/i18n";

const ICON_EMOJI: Record<string, string> = {
  tree: "🌳",
  garden: "🌷",
  water: "💧",
  recycle: "♻️",
  star: "⭐",
  home: "🏠",
  air: "💨",
  leaf: "🍃",
  solar: "☀️",
  crown: "👑",
};

export function ProfilePage() {
  const { player, updateProfile } = useAuthStore();
  const [achievements, setAchievements] = useState<PlayerAchievement[]>([]);
  const [allCount, setAllCount] = useState(0);
  const [editing, setEditing] = useState(false);
  const [nickname, setNickname] = useState(player?.nickname ?? "");

  useEffect(() => {
    gameApi.getMyAchievements().then(({ data }) => setAchievements(data.results));
    gameApi.getAchievements().then(({ data }) => setAllCount(data.count));
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
          <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center text-3xl">
            🌿
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
              {achievements.length}/{allCount}
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
              <span className="text-3xl">{ICON_EMOJI[pa.achievement.icon] ?? "🏆"}</span>
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
