import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { GoogleLoginButton } from "@/components/GoogleLoginButton";
import { useAuthStore } from "@/stores/authStore";
import { t } from "@/i18n";

export function LoginPage() {
  const { login, isLoading } = useAuthStore();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await login({ username, password });
      navigate("/");
    } catch {
      setError("Foydalanuvchi nomi yoki parol noto'g'ri.");
    }
  };

  return (
    <div className="max-w-md mx-auto mt-16">
      <div className="bg-white rounded-2xl shadow-lg p-8">
        <h1 className="text-2xl font-bold text-green-700 mb-6 text-center">
          {t("auth.login_title")}
        </h1>

        {error && (
          <div className="bg-red-50 text-red-600 rounded-lg p-3 mb-4 text-sm">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t("auth.username")}
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-400"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t("auth.password")}
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-400"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="bg-green-600 hover:bg-green-500 disabled:bg-gray-400 text-white font-semibold py-3 rounded-lg transition-colors"
          >
            {isLoading ? "Kirilmoqda..." : t("menu.login")}
          </button>
        </form>

        <div className="flex items-center gap-3 my-5">
          <div className="flex-1 h-px bg-gray-200" />
          <span className="text-sm text-gray-400">yoki</span>
          <div className="flex-1 h-px bg-gray-200" />
        </div>

        <div className="flex justify-center">
          <GoogleLoginButton />
        </div>

        <p className="text-center text-sm text-gray-500 mt-4">
          {t("auth.no_account")}{" "}
          <Link to="/register" className="text-green-600 hover:underline">
            {t("menu.register")}
          </Link>
        </p>
      </div>
    </div>
  );
}
