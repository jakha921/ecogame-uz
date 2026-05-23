import { create } from "zustand";
import { gameApi } from "@/api/game";
import type { Achievement, EcoAction, EcosystemState, GameProgress, GameSession, Level } from "@/api/types";

interface GameState {
  currentLevel: Level | null;
  currentSession: GameSession | null;
  progress: GameProgress | null;
  ecosystem: EcosystemState;
  score: number;
  levels: Level[];
  actions: EcoAction[];
  achievements: Achievement[];
  isPlaying: boolean;
  isLoading: boolean;

  loadLevels: () => Promise<void>;
  loadActions: (levelNumber?: number) => Promise<void>;
  loadAchievements: () => Promise<void>;
  startGame: (levelId: number) => Promise<GameSession>;
  endGame: () => Promise<void>;
  updateEcosystem: (state: EcosystemState) => void;
  addScore: (points: number) => void;
  syncProgress: () => Promise<void>;
  setProgress: (progress: GameProgress) => void;
  reset: () => void;
}

const DEFAULT_ECOSYSTEM: EcosystemState = { air: 0, water: 0, soil: 0, biodiversity: 0 };

export const useGameStore = create<GameState>((set, get) => ({
  currentLevel: null,
  currentSession: null,
  progress: null,
  ecosystem: DEFAULT_ECOSYSTEM,
  score: 0,
  levels: [],
  actions: [],
  achievements: [],
  isPlaying: false,
  isLoading: false,

  loadLevels: async () => {
    const { data } = await gameApi.getLevels();
    set({ levels: data.results });
  },

  loadActions: async (levelNumber) => {
    const { data } = await gameApi.getActions(levelNumber);
    set({ actions: data.results });
  },

  loadAchievements: async () => {
    const { data } = await gameApi.getAchievements();
    set({ achievements: data.results });
  },

  startGame: async (levelId) => {
    set({ isLoading: true });
    try {
      const { data: session } = await gameApi.startSession(levelId);
      const level = get().levels.find((l) => l.id === levelId) ?? session.level;
      const ecosystem = level.ecosystem_initial;
      set({
        currentSession: session,
        currentLevel: level,
        ecosystem,
        score: 0,
        isPlaying: true,
      });
      return session;
    } finally {
      set({ isLoading: false });
    }
  },

  endGame: async () => {
    const session = get().currentSession;
    if (!session) return;
    try {
      const { data: progress } = await gameApi.endSession(session.id);
      set({ progress, isPlaying: false });
    } finally {
      set({ currentSession: null, isPlaying: false });
    }
  },

  updateEcosystem: (ecosystem) => set({ ecosystem }),

  addScore: (points) => set((state) => ({ score: state.score + points })),

  syncProgress: async () => {
    const session = get().currentSession;
    if (!session) return;
    // Sync is driven by ActionSubmitView — this re-fetches latest progress
    const { data } = await gameApi.getProgress();
    const prog = data.results.find((p) => p.level.id === session.level.id);
    if (prog) set({ progress: prog });
  },

  setProgress: (progress) => {
    set({
      progress,
      score: progress.score,
      ecosystem: {
        air: progress.air_quality,
        water: progress.water_purity,
        soil: progress.soil_health,
        biodiversity: progress.biodiversity,
      },
    });
  },

  reset: () =>
    set({
      currentLevel: null,
      currentSession: null,
      progress: null,
      ecosystem: DEFAULT_ECOSYSTEM,
      score: 0,
      isPlaying: false,
    }),
}));
