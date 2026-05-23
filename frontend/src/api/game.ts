import type {
  Achievement,
  ActionItem,
  EcoAction,
  GameProgress,
  GameSession,
  Level,
  PaginatedResponse,
  PlayerAchievement,
} from "./types";
import { apiClient } from "./client";

export const gameApi = {
  getLevels: () => apiClient.get<PaginatedResponse<Level>>("/game/levels/"),
  getLevel: (id: number) => apiClient.get<Level>(`/game/levels/${id}/`),
  getActions: (levelNumber?: number) =>
    apiClient.get<PaginatedResponse<EcoAction>>("/game/actions/", {
      params: levelNumber ? { level: levelNumber } : undefined,
    }),
  getProgress: () => apiClient.get<PaginatedResponse<GameProgress>>("/game/progress/"),
  startSession: (levelId: number) =>
    apiClient.post<GameSession>("/game/sessions/start/", { level_id: levelId }),
  endSession: (sessionId: number) =>
    apiClient.post<GameProgress>(`/game/sessions/${sessionId}/end/`),
  submitActions: (sessionId: number, actions: ActionItem[]) =>
    apiClient.post<GameProgress>(`/game/sessions/${sessionId}/actions/`, { actions }),
  getAchievements: () => apiClient.get<PaginatedResponse<Achievement>>("/game/achievements/"),
  getMyAchievements: () =>
    apiClient.get<PaginatedResponse<PlayerAchievement>>("/game/achievements/my/"),
};
