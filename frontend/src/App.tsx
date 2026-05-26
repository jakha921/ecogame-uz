import { useEffect } from "react";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Layout } from "@/components/Layout";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { useAuthStore } from "@/stores/authStore";
import { EducationDetailPage } from "@/pages/EducationDetailPage";
import { EducationPage } from "@/pages/EducationPage";
import { LeaderboardPage } from "@/pages/LeaderboardPage";
import { LoginPage } from "@/pages/LoginPage";
import { MainMenu } from "@/pages/MainMenu";
import { ProfilePage } from "@/pages/ProfilePage";
import { QuizPlayPage } from "@/pages/QuizPlayPage";
import { QuizResultsPage } from "@/pages/QuizResultsPage";
import { RegisterPage } from "@/pages/RegisterPage";
import { EcoSortingPage } from "@/pages/EcoSortingPage";


export default function App() {
  const initFromStorage = useAuthStore((s) => s.initFromStorage);

  useEffect(() => {
    initFromStorage();
  }, [initFromStorage]);

  return (
    <GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID ?? ""}>
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<MainMenu />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/leaderboard" element={<LeaderboardPage />} />
          <Route path="/education" element={<EducationPage />} />
          <Route path="/education/:id" element={<EducationDetailPage />} />
          <Route
            path="/quiz/quick"
            element={
              <ProtectedRoute>
                <QuizPlayPage mode="QUICK" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/quiz/category/:category"
            element={
              <ProtectedRoute>
                <QuizPlayPage mode="CATEGORY" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/quiz/daily"
            element={
              <ProtectedRoute>
                <QuizPlayPage mode="DAILY" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/quiz/marathon"
            element={
              <ProtectedRoute>
                <QuizPlayPage mode="MARATHON" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/quiz/results/:sessionId"
            element={
              <ProtectedRoute>
                <QuizResultsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/mini-game/sort"
            element={
              <ProtectedRoute>
                <EcoSortingPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />
        </Route>
      </Routes>
    </BrowserRouter>
    </GoogleOAuthProvider>
  );
}
