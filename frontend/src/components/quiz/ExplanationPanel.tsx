import { useNavigate } from "react-router-dom";
import { BookOpen, CheckCircle, XCircle } from "lucide-react";

interface ExplanationPanelProps {
  isCorrect: boolean;
  explanation: string;
  pointsEarned: number;
  onNext: () => void;
  articleId?: number;
}

export function ExplanationPanel({
  isCorrect,
  explanation,
  pointsEarned,
  onNext,
  articleId,
}: ExplanationPanelProps) {
  const navigate = useNavigate();

  return (
    <div
      className={[
        "rounded-2xl border-2 p-5 flex flex-col gap-4",
        isCorrect
          ? "bg-green-50 border-green-300"
          : "bg-red-50 border-red-300",
      ].join(" ")}
    >
      <div className="flex items-center gap-3">
        {isCorrect ? (
          <CheckCircle size={24} className="text-green-600 flex-shrink-0" />
        ) : (
          <XCircle size={24} className="text-red-500 flex-shrink-0" />
        )}
        <div>
          <p className={`font-bold ${isCorrect ? "text-green-700" : "text-red-700"}`}>
            {isCorrect ? "To'g'ri!" : "Noto'g'ri"}
          </p>
          {isCorrect && pointsEarned > 0 && (
            <p className="text-xs text-green-600">+{pointsEarned} ball</p>
          )}
        </div>
      </div>

      <p className="text-sm text-gray-700 leading-relaxed">{explanation}</p>

      <div className="flex items-center gap-3 flex-wrap">
        {articleId && (
          <button
            onClick={() => navigate(`/education/${articleId}`)}
            className="flex items-center gap-1.5 text-sm text-blue-600 hover:underline"
          >
            <BookOpen size={14} />
            Maqolani o'qish
          </button>
        )}
        <button
          onClick={onNext}
          className="ml-auto bg-green-600 hover:bg-green-500 text-white font-semibold text-sm px-5 py-2 rounded-xl transition-colors"
        >
          Keyingi
        </button>
      </div>
    </div>
  );
}
