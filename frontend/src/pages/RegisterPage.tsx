import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import { t } from "@/i18n";

export function RegisterPage() {
  const { register, isLoading } = useAuthStore();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: "",
    nickname: "",
    email: "",
    password: "",
    password_confirm: "",
  });
  const [error, setError] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (form.password !== form.password_confirm) {
      setError("Parollar mos kelmadi.");
      return;
    }
    try {
      await register(form);
      navigate("/");
    } catch (err: unknown) {
      const msg =
        err && typeof err === "object" && "response" in err
          ? // @ts-expect-error axios error shape
            JSON.stringify(err.response?.data)
          : "Ro'yxatdan o'tishda xatolik.";
      setError(msg);
    }
  };

  const fields: { name: keyof typeof form; label: string; type: string }[] = [
    { name: "username", label: t("auth.username"), type: "text" },
    { name: "nickname", label: t("auth.nickname"), type: "text" },
    { name: "email", label: t("auth.email"), type: "email" },
    { name: "password", label: t("auth.password"), type: "password" },
    { name: "password_confirm", label: t("auth.confirm_password"), type: "password" },
  ];

  return (
    <div className="max-w-md mx-auto mt-12">
      <div className="bg-white rounded-2xl shadow-lg p-8">
        <h1 className="text-2xl font-bold text-green-700 mb-6 text-center">
          {t("auth.register_title")}
        </h1>

        {error && (
          <div className="bg-red-50 text-red-600 rounded-lg p-3 mb-4 text-sm">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {fields.map(({ name, label, type }) => (
            <div key={name}>
              <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
              <input
                type={type}
                name={name}
                value={form[name]}
                onChange={handleChange}
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-400"
              />
            </div>
          ))}

          <button
            type="submit"
            disabled={isLoading}
            className="bg-green-600 hover:bg-green-500 disabled:bg-gray-400 text-white font-semibold py-2 rounded-lg transition-colors"
          >
            {isLoading ? "Ro'yxatdan o'tilmoqda..." : t("menu.register")}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-4">
          {t("auth.has_account")}{" "}
          <Link to="/login" className="text-green-600 hover:underline">
            {t("menu.login")}
          </Link>
        </p>
      </div>
    </div>
  );
}
