import { useState } from "react";
import { Link, Outlet, useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import { t } from "@/i18n";

export function Layout() {
  const { isAuthenticated, player, logout } = useAuthStore();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-emerald-50">
      <header className="bg-green-700 text-white shadow-md">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/" className="text-xl font-bold flex items-center gap-2">
            🌿 {t("app_name")}
          </Link>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-6 text-sm font-medium">
            <Link to="/" className="hover:text-green-200 transition-colors">
              {t("menu.home")}
            </Link>
            <Link to="/leaderboard" className="hover:text-green-200 transition-colors">
              {t("menu.leaderboard")}
            </Link>
            <Link to="/education" className="hover:text-green-200 transition-colors">
              {t("menu.education")}
            </Link>
            {isAuthenticated ? (
              <>
                <Link to="/profile" className="hover:text-green-200 transition-colors">
                  {player?.nickname ?? t("menu.profile")}
                </Link>
                <button
                  onClick={handleLogout}
                  className="bg-green-600 hover:bg-green-500 px-3 py-1 rounded transition-colors"
                >
                  {t("menu.logout")}
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="bg-green-600 hover:bg-green-500 px-3 py-1 rounded transition-colors"
                >
                  {t("menu.login")}
                </Link>
                <Link
                  to="/register"
                  className="bg-emerald-500 hover:bg-emerald-400 px-3 py-1 rounded transition-colors"
                >
                  {t("menu.register")}
                </Link>
              </>
            )}
          </nav>

          {/* Mobile hamburger */}
          <button
            className="md:hidden text-white"
            onClick={() => setMenuOpen((o) => !o)}
            aria-label="Menu"
          >
            <span className="text-2xl">{menuOpen ? "✕" : "☰"}</span>
          </button>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="md:hidden bg-green-800 px-4 pb-4 flex flex-col gap-3 text-sm">
            <Link to="/" onClick={() => setMenuOpen(false)}>
              {t("menu.home")}
            </Link>
            <Link to="/leaderboard" onClick={() => setMenuOpen(false)}>
              {t("menu.leaderboard")}
            </Link>
            <Link to="/education" onClick={() => setMenuOpen(false)}>
              {t("menu.education")}
            </Link>
            {isAuthenticated ? (
              <>
                <Link to="/profile" onClick={() => setMenuOpen(false)}>
                  {t("menu.profile")}
                </Link>
                <button onClick={handleLogout} className="text-left">
                  {t("menu.logout")}
                </button>
              </>
            ) : (
              <>
                <Link to="/login" onClick={() => setMenuOpen(false)}>
                  {t("menu.login")}
                </Link>
                <Link to="/register" onClick={() => setMenuOpen(false)}>
                  {t("menu.register")}
                </Link>
              </>
            )}
          </div>
        )}
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
