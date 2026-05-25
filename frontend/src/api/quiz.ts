import { apiClient } from "./client";
import type {
  Achievement,
  ActionCategory,
  AnswerResult,
  DailyChallenge,
  PaginatedResponse,
  PlayerAchievement,
  PlayerStats,
  Question,
  QuizMode,
  QuizResult,
  QuizSession,
} from "./types";

export const quizApi = {
  getQuestions: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<Question>>("/game/quiz/questions/", { params }),

  startSession: (data: { mode: QuizMode; category?: ActionCategory }) =>
    apiClient.post<QuizSession & { session_id: number; questions: Question[] }>(
      "/game/quiz/sessions/",
      data,
    ),

  submitAnswer: (
    sessionId: number,
    data: { question_id: number; answer_id: number | null; time_spent_ms: number },
  ) => apiClient.post<AnswerResult>(`/game/quiz/sessions/${sessionId}/answer/`, data),

  endSession: (sessionId: number) =>
    apiClient.post<QuizResult>(`/game/quiz/sessions/${sessionId}/end/`),

  getDailyChallenge: () => apiClient.get<DailyChallenge>("/game/quiz/daily/"),

  getStats: () => apiClient.get<PlayerStats>("/game/quiz/stats/"),

  getAchievements: () => apiClient.get<PaginatedResponse<Achievement>>("/game/achievements/"),

  getMyAchievements: () =>
    apiClient.get<PlayerAchievement[]>("/game/achievements/my/"),

  submitMiniGameScore: (data: {
    score: number;
    correct_count: number;
    total_items: number;
  }) => apiClient.post("/game/mini-game/sort/score/", data),
};
