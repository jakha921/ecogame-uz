import { create } from "zustand";
import { authApi } from "@/api/auth";
import type { LoginData, Player, RegisterData } from "@/api/types";

interface AuthState {
  player: Player | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (data: LoginData) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  fetchProfile: () => Promise<void>;
  updateProfile: (data: Partial<Pick<Player, "nickname" | "avatar" | "email">>) => Promise<void>;
  initFromStorage: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  player: null,
  accessToken: localStorage.getItem("access_token"),
  refreshToken: localStorage.getItem("refresh_token"),
  isAuthenticated: !!localStorage.getItem("access_token"),
  isLoading: false,

  login: async (data) => {
    set({ isLoading: true });
    try {
      const { data: tokens } = await authApi.login(data);
      localStorage.setItem("access_token", tokens.access);
      localStorage.setItem("refresh_token", tokens.refresh);
      set({ accessToken: tokens.access, refreshToken: tokens.refresh, isAuthenticated: true });
      await get().fetchProfile();
    } finally {
      set({ isLoading: false });
    }
  },

  register: async (data) => {
    set({ isLoading: true });
    try {
      await authApi.register(data);
      await get().login({ username: data.username, password: data.password });
    } finally {
      set({ isLoading: false });
    }
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    set({ player: null, accessToken: null, refreshToken: null, isAuthenticated: false });
  },

  fetchProfile: async () => {
    try {
      const { data: player } = await authApi.getProfile();
      set({ player });
    } catch {
      get().logout();
    }
  },

  updateProfile: async (data) => {
    const { data: player } = await authApi.updateProfile(data);
    set({ player });
  },

  initFromStorage: async () => {
    const token = localStorage.getItem("access_token");
    if (token && !get().player) {
      await get().fetchProfile();
    }
  },
}));
