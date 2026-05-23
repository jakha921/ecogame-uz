import type { LeaderboardEntry, PaginatedResponse } from "./types";
import { apiClient } from "./client";

export const leaderboardApi = {
  getLeaderboard: (page?: number) =>
    apiClient.get<PaginatedResponse<LeaderboardEntry>>("/leaderboard/", {
      params: page ? { page } : undefined,
    }),
  getMyRank: () => apiClient.get<LeaderboardEntry>("/leaderboard/me/"),
};
