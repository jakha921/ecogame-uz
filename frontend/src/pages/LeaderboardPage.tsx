import { useEffect, useState } from "react";
import { leaderboardApi } from "@/api/leaderboard";
import type { LeaderboardEntry } from "@/api/types";
import { useAuthStore } from "@/stores/authStore";
import { t } from "@/i18n";

export function LeaderboardPage() {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [myRank, setMyRank] = useState<LeaderboardEntry | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { player, isAuthenticated } = useAuthStore();

  useEffect(() => {
    leaderboardApi
      .getLeaderboard()
      .then(({ data }) => setEntries(data.results))
      .finally(() => setIsLoading(false));

    if (isAuthenticated) {
      leaderboardApi.getMyRank().then(({ data }) => setMyRank(data)).catch(() => null);
    }
  }, [isAuthenticated]);

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-green-700">{t("leaderboard.title")}</h1>

      {myRank && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-4">
          <p className="text-sm font-semibold text-green-600 mb-1">{t("leaderboard.my_rank")}</p>
          <div className="flex gap-6 text-sm">
            <span>#{myRank.rank}</span>
            <span className="font-bold">{myRank.player_nickname}</span>
            <span>{myRank.total_score} ball</span>
          </div>
        </div>
      )}

      {isLoading ? (
        <p className="text-gray-400 text-center py-12">Yuklanmoqda...</p>
      ) : (
        <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-green-50">
              <tr>
                <th className="px-4 py-3 text-left text-gray-500">{t("leaderboard.rank")}</th>
                <th className="px-4 py-3 text-left text-gray-500">{t("leaderboard.player")}</th>
                <th className="px-4 py-3 text-right text-gray-500">{t("leaderboard.score")}</th>
                <th className="px-4 py-3 text-right text-gray-500 hidden sm:table-cell">
                  {t("leaderboard.levels")}
                </th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry) => {
                const isMe = player?.nickname === entry.player_nickname;
                return (
                  <tr
                    key={entry.rank}
                    className={`border-t ${isMe ? "bg-green-50 font-semibold" : "hover:bg-gray-50"}`}
                  >
                    <td className="px-4 py-3">
                      {entry.rank <= 3 ? (
                        <span>{["🥇", "🥈", "🥉"][entry.rank - 1]}</span>
                      ) : (
                        `#${entry.rank}`
                      )}
                    </td>
                    <td className="px-4 py-3">{entry.player_nickname}</td>
                    <td className="px-4 py-3 text-right">{entry.total_score}</td>
                    <td className="px-4 py-3 text-right hidden sm:table-cell">
                      {entry.levels_completed}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
