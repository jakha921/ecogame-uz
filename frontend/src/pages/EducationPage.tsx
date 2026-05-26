import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bird, BookOpen, Droplets, Recycle, SunMedium, TreeDeciduous } from "lucide-react";
import { educationApi } from "@/api/education";
import type { ActionCategory, EducationalContent } from "@/api/types";
import { t } from "@/i18n";

const CATEGORIES: { key: ActionCategory | "ALL"; label: string }[] = [
  { key: "ALL", label: t("education.all") },
  { key: "FLORA", label: "O'simliklar" },
  { key: "WATER", label: "Suv" },
  { key: "WASTE", label: "Chiqindilar" },
  { key: "ENERGY", label: "Energiya" },
  { key: "FAUNA", label: "Hayvonlar" },
];

const CATEGORY_ICON: Record<string, React.ReactNode> = {
  FLORA: <TreeDeciduous size={18} className="text-green-600" />,
  WATER: <Droplets size={18} className="text-blue-600" />,
  WASTE: <Recycle size={18} className="text-yellow-600" />,
  ENERGY: <SunMedium size={18} className="text-orange-500" />,
  FAUNA: <Bird size={18} className="text-purple-600" />,
};

export function EducationPage() {
  const [articles, setArticles] = useState<EducationalContent[]>([]);
  const [selected, setSelected] = useState<ActionCategory | "ALL">("ALL");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setIsLoading(true);
    educationApi
      .getArticles(selected === "ALL" ? undefined : selected)
      .then(({ data }) => setArticles(data.results))
      .finally(() => setIsLoading(false));
  }, [selected]);

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-green-700">{t("education.title")}</h1>

      {/* Category tabs */}
      <div className="flex gap-2 flex-wrap">
        {CATEGORIES.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setSelected(key)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
              selected === key
                ? "bg-green-600 text-white"
                : "bg-white border border-gray-200 text-gray-600 hover:border-green-400"
            }`}
          >
            {key !== "ALL" && <span className="inline-flex">{CATEGORY_ICON[key]}</span>} {label}
          </button>
        ))}
      </div>

      {isLoading ? (
        <p className="text-gray-400 text-center py-12">Yuklanmoqda...</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {articles.map((article) => (
            <Link
              key={article.id}
              to={`/education/${article.id}`}
              className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 hover:shadow-md hover:border-green-200 transition-all flex flex-col gap-2"
            >
              <div>{CATEGORY_ICON[article.category] ?? <BookOpen size={20} className="text-gray-500" />}</div>
              <h2 className="font-bold text-gray-800">{article.title_uz}</h2>
              <p className="text-sm text-gray-500 line-clamp-3">
                {article.body_uz.slice(0, 120)}...
              </p>
              <span className="text-green-600 text-sm font-medium mt-auto">
                {t("education.read_more")} →
              </span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
