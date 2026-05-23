import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { educationApi } from "@/api/education";
import type { EducationalContent } from "@/api/types";

export function EducationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [article, setArticle] = useState<EducationalContent | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (!id) return;
    educationApi
      .getArticle(Number(id))
      .then(({ data }) => setArticle(data))
      .catch(() => navigate("/education"))
      .finally(() => setIsLoading(false));
  }, [id, navigate]);

  if (isLoading) return <p className="text-gray-400 text-center py-16">Yuklanmoqda...</p>;
  if (!article) return null;

  return (
    <div className="max-w-2xl mx-auto">
      <button
        onClick={() => navigate(-1)}
        className="text-green-600 text-sm mb-4 hover:underline"
      >
        ← Orqaga
      </button>
      <div className="bg-white rounded-2xl shadow-sm p-8">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">{article.title_uz}</h1>
        <div className="text-gray-700 leading-relaxed whitespace-pre-line">{article.body_uz}</div>
      </div>
    </div>
  );
}
