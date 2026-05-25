import { useEffect } from "react";
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
import { RegisterPage } from "@/pages/RegisterPage";

function ComingSoon({ title }: { title: string }) {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">{title}</h2>
        <p className="text-muted-foreground">Tez orada...</p>
      </div>
    </div>
  );
}

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
            path="/quiz/quick"
            element={
              <ProtectedRoute>
                <ComingSoon title="Tezkor viktorina" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/quiz/category/:category"
            element={
              <ProtectedRoute>
                <ComingSoon title="Kategoriya viktorinasi" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/quiz/daily"
            element={
              <ProtectedRoute>
                <ComingSoon title="Kunlik topshiriq" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/quiz/marathon"
            element={
              <ProtectedRoute>
                <ComingSoon title="Marafon rejimi" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/quiz/results/:sessionId"
            element={
              <ProtectedRoute>
                <ComingSoon title="Natijalar" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/mini-game/sort"
            element={
              <ProtectedRoute>
                <ComingSoon title="Chiqindilarni saralash" />
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
