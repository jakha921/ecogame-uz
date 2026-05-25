import { create } from "zustand";
import { quizApi } from "@/api/quiz";
import type {
  ActionCategory,
  AnswerResult,
  DailyChallenge,
  PlayerStats,
  Question,
  QuizMode,
  QuizResult,
  QuizSession,
} from "@/api/types";

interface QuizState {
  currentSession: QuizSession | null;
  questions: Question[];
  currentQuestionIndex: number;
  lastResult: AnswerResult | null;
  showExplanation: boolean;
  score: number;
  streak: number;
  correctCount: number;
  quizResult: QuizResult | null;
  playerStats: PlayerStats | null;
  dailyChallenge: DailyChallenge | null;
  isLoading: boolean;
  error: string | null;
}

interface QuizActions {
  startQuiz: (mode: QuizMode, category?: ActionCategory) => Promise<void>;
  submitAnswer: (
    questionId: number,
    answerId: number | null,
    timeSpentMs: number,
  ) => Promise<AnswerResult | null>;
  nextQuestion: () => void;
  endQuiz: () => Promise<QuizResult | null>;
  loadStats: () => Promise<void>;
  loadDailyChallenge: () => Promise<void>;
  reset: () => void;
}

const initialState: QuizState = {
  currentSession: null,
  questions: [],
  currentQuestionIndex: 0,
  lastResult: null,
  showExplanation: false,
  score: 0,
  streak: 0,
  correctCount: 0,
  quizResult: null,
  playerStats: null,
  dailyChallenge: null,
  isLoading: false,
  error: null,
};

export const useQuizStore = create<QuizState & QuizActions>((set, get) => ({
  ...initialState,

  startQuiz: async (mode, category) => {
    set({ isLoading: true, error: null });
    try {
      const response = await quizApi.startSession({ mode, category });
      const { questions, session_id, ...session } = response.data;
      set({
        currentSession: { ...session, id: session_id ?? session.id },
        questions: questions ?? [],
        currentQuestionIndex: 0,
        score: 0,
        streak: 0,
        correctCount: 0,
        lastResult: null,
        showExplanation: false,
        quizResult: null,
        isLoading: false,
      });
    } catch {
      set({ isLoading: false, error: "Viktorinani boshlashda xato yuz berdi" });
    }
  },

  submitAnswer: async (questionId, answerId, timeSpentMs) => {
    const { currentSession } = get();
    if (!currentSession) return null;
    try {
      const response = await quizApi.submitAnswer(currentSession.id, {
        question_id: questionId,
        answer_id: answerId,
        time_spent_ms: timeSpentMs,
      });
      const result = response.data;
      set((s) => ({
        lastResult: result,
        showExplanation: true,
        score: result.total_score,
        streak: result.streak,
        correctCount: result.is_correct ? s.correctCount + 1 : s.correctCount,
        currentSession: s.currentSession
          ? { ...s.currentSession, score: result.total_score }
          : null,
      }));
      return result;
    } catch {
      set({ error: "Javob yuborishda xato" });
      return null;
    }
  },

  nextQuestion: () => {
    set((s) => ({
      currentQuestionIndex: s.currentQuestionIndex + 1,
      lastResult: null,
      showExplanation: false,
    }));
  },

  endQuiz: async () => {
    const { currentSession } = get();
    if (!currentSession) return null;
    set({ isLoading: true });
    try {
      const response = await quizApi.endSession(currentSession.id);
      const result = response.data;
      set({ quizResult: result, isLoading: false });
      return result;
    } catch {
      set({ isLoading: false, error: "Viktorinani tugatishda xato" });
      return null;
    }
  },

  loadStats: async () => {
    set({ isLoading: true });
    try {
      const response = await quizApi.getStats();
      set({ playerStats: response.data, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },

  loadDailyChallenge: async () => {
    set({ isLoading: true });
    try {
      const response = await quizApi.getDailyChallenge();
      set({ dailyChallenge: response.data, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },

  reset: () => set(initialState),
}));
