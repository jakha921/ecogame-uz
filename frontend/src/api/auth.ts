import type { AuthTokens, LoginData, Player, RegisterData } from "./types";
import { apiClient } from "./client";

export const authApi = {
  register: (data: RegisterData) => apiClient.post<Player>("/auth/register/", data),
  login: (data: LoginData) => apiClient.post<AuthTokens>("/auth/login/", data),
  refreshToken: (refresh: string) =>
    apiClient.post<{ access: string }>("/auth/token/refresh/", { refresh }),
  getProfile: () => apiClient.get<Player>("/auth/me/"),
  updateProfile: (data: Partial<Pick<Player, "nickname" | "avatar" | "email">>) =>
    apiClient.patch<Player>("/auth/me/", data),
};
