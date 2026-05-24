import type { AuthTokens, LoginData, Player, RegisterData } from "./types";
import { apiClient } from "./client";

export interface AnonymousTokens extends AuthTokens {
  session_key: string;
  is_anonymous: boolean;
}

export const authApi = {
  register: (data: RegisterData) => apiClient.post<Player>("/auth/register/", data),
  login: (data: LoginData) => apiClient.post<AuthTokens>("/auth/login/", data),
  loginAnonymous: (sessionKey?: string) =>
    apiClient.post<AnonymousTokens>("/auth/anonymous/", sessionKey ? { session_key: sessionKey } : {}),
  claimAccount: (data: { username: string; nickname: string; password: string }) =>
    apiClient.post<Player>("/auth/claim/", data),
  refreshToken: (refresh: string) =>
    apiClient.post<{ access: string }>("/auth/token/refresh/", { refresh }),
  getProfile: () => apiClient.get<Player>("/auth/me/"),
  updateProfile: (data: Partial<Pick<Player, "nickname" | "avatar" | "email">>) =>
    apiClient.patch<Player>("/auth/me/", data),
};
