import { useEffect } from "react";
import { useAuthStore } from "@/stores/authStore";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

// Auto-creates an anonymous session if not authenticated — no login redirect needed
export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, loginAnonymous } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated && !isLoading) {
      loginAnonymous();
    }
  }, [isAuthenticated, isLoading, loginAnonymous]);

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-[40vh]">
        <p className="text-gray-400 text-sm">Yuklanmoqda...</p>
      </div>
    );
  }

  return <>{children}</>;
}
