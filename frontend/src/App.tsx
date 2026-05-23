import { useEffect } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Layout } from "@/components/Layout";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { useAuthStore } from "@/stores/authStore";
import { EducationDetailPage } from "@/pages/EducationDetailPage";
import { EducationPage } from "@/pages/EducationPage";
import { GamePage } from "@/pages/GamePage";
import { LeaderboardPage } from "@/pages/LeaderboardPage";
import { LoginPage } from "@/pages/LoginPage";
import { MainMenu } from "@/pages/MainMenu";
import { ProfilePage } from "@/pages/ProfilePage";
import { RegisterPage } from "@/pages/RegisterPage";

export default function App() {
  const initFromStorage = useAuthStore((s) => s.initFromStorage);

  useEffect(() => {
    initFromStorage();
  }, [initFromStorage]);

  return (
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
            path="/play/:levelId"
            element={
              <ProtectedRoute>
                <GamePage />
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
  );
}
