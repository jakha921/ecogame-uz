// ─── Auth ────────────────────────────────────────────────────────────────────

export interface Player {
  id: number;
  username: string;
  nickname: string;
  email: string;
  avatar: string;
  total_score: number;
  date_joined: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface RegisterData {
  username: string;
  nickname: string;
  email: string;
  password: string;
  password_confirm: string;
}

export interface LoginData {
  username: string;
  password: string;
}

// ─── Shared ──────────────────────────────────────────────────────────────────

export type ActionCategory = "FLORA" | "WATER" | "WASTE" | "ENERGY" | "FAUNA";

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// ─── Quiz ─────────────────────────────────────────────────────────────────────

export type QuestionType = "MCQ" | "TRUE_FALSE" | "SCENARIO";
export type QuizMode = "QUICK" | "CATEGORY" | "DAILY" | "MARATHON";

export interface Answer {
  id: number;
  text_uz: string;
  order: number;
}

export interface Question {
  id: number;
  text_uz: string;
  category: ActionCategory;
  difficulty: 1 | 2 | 3;
  question_type: QuestionType;
  explanation_uz: string;
  time_limit: number;
  answers: Answer[];
}

export interface QuizSession {
  id: number;
  mode: QuizMode;
  category: ActionCategory | null;
  score: number;
  correct_count: number;
  total_questions: number;
  current_streak: number;
  max_streak: number;
  started_at: string;
  finished_at: string | null;
}

export interface AnswerResult {
  is_correct: boolean;
  correct_answer_id: number | null;
  explanation_uz: string;
  points_earned: number;
  streak: number;
  streak_multiplier: number;
  time_bonus: number;
  total_score: number;
  is_game_over: boolean;
}

export interface QuizResult {
  session: QuizSession;
  accuracy: number;
  rank_title: string;
  achievements_unlocked: Achievement[];
}

export interface PlayerStats {
  total_quizzes: number;
  total_correct: number;
  accuracy_pct: number;
  best_streak: number;
  daily_streak: number;
  rank_title: string;
  per_category: Record<ActionCategory, { total: number; correct: number; accuracy: number }>;
}

export interface DailyChallenge {
  id: number;
  date: string;
  bonus_score: number;
  is_completed: boolean;
  questions: Question[];
}

export interface SortingItem {
  id: number;
  name_uz: string;
  image: string;
  correct_bin: "plastic" | "glass" | "organic" | "paper" | "battery";
}

// ─── Achievements ─────────────────────────────────────────────────────────────

export type ConditionType =
  | "SCORE"
  | "QUIZ_COUNT"
  | "STREAK"
  | "DAILY_STREAK"
  | "CATEGORY_MASTER";

export interface Achievement {
  id: number;
  key: string;
  name_uz: string;
  description_uz: string;
  icon: string;
  condition_type: ConditionType;
}

export interface PlayerAchievement {
  id: number;
  achievement: Achievement;
  unlocked_at: string;
}

// ─── Leaderboard ──────────────────────────────────────────────────────────────

export interface LeaderboardEntry {
  rank: number;
  player_nickname: string;
  player_avatar: string;
  total_score: number;
  levels_completed: number;
  achievements_count: number;
}

// ─── Education ────────────────────────────────────────────────────────────────

export interface EducationalContent {
  id: number;
  title_uz: string;
  body_uz: string;
  category: ActionCategory;
  image: string | null;
  order: number;
}

export interface EcoFact {
  id: number;
  text_uz: string;
  source: string;
  category: ActionCategory;
}
