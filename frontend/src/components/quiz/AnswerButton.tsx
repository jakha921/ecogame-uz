import { CheckCircle, XCircle } from "lucide-react";
import type { Answer } from "@/api/types";

type AnswerState = "idle" | "selected" | "correct" | "incorrect";

interface AnswerButtonProps {
  answer: Answer;
  state: AnswerState;
  onClick: () => void;
  disabled: boolean;
}

const STATE_STYLES: Record<AnswerState, string> = {
  idle: "border-gray-200 bg-white hover:border-green-400 hover:bg-green-50 text-gray-800",
  selected: "border-blue-400 bg-blue-50 text-blue-800",
  correct: "border-green-500 bg-green-50 text-green-800",
  incorrect: "border-red-400 bg-red-50 text-red-800",
};

export function AnswerButton({ answer, state, onClick, disabled }: AnswerButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={[
        "w-full border-2 rounded-xl px-4 py-3 text-sm font-medium text-left transition-all",
        "flex items-center justify-between gap-2",
        "disabled:cursor-default",
        STATE_STYLES[state],
      ].join(" ")}
    >
      <span>{answer.text_uz}</span>
      {state === "correct" && <CheckCircle size={18} className="text-green-600 flex-shrink-0" />}
      {state === "incorrect" && <XCircle size={18} className="text-red-500 flex-shrink-0" />}
    </button>
  );
}
