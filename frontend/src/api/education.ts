import type { ActionCategory, EcoFact, EducationalContent, PaginatedResponse } from "./types";
import { apiClient } from "./client";

export const educationApi = {
  getArticles: (category?: ActionCategory) =>
    apiClient.get<PaginatedResponse<EducationalContent>>("/education/articles/", {
      params: category ? { category } : undefined,
    }),
  getArticle: (id: number) => apiClient.get<EducationalContent>(`/education/articles/${id}/`),
  getRandomFact: () => apiClient.get<EcoFact | Record<string, never>>("/education/facts/random/"),
};
