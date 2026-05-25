import type { Question } from "@/api/types";
import { AnswerButton } from "./AnswerButton";

type AnswerState = "idle" | "selected" | "correct" | "incorrect";

interface QuestionCardProps {
  question: Question;
  onAnswer: (answerId: number | null) => void;
  answerState: Record<number, AnswerState>;
  disabled: boolean;
}

export function QuestionCard({ question, onAnswer, answerState, disabled }: QuestionCardProps) {
  const isTrueFalse = question.question_type === "TRUE_FALSE";

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 flex flex-col gap-5">
      <p className="text-base font-semibold text-gray-800 leading-relaxed">{question.text_uz}</p>

      <div className={isTrueFalse ? "flex gap-3" : "grid grid-cols-1 sm:grid-cols-2 gap-3"}>
        {question.answers.map((answer) => (
          <AnswerButton
            key={answer.id}
            answer={answer}
            state={answerState[answer.id] ?? "idle"}
            onClick={() => onAnswer(answer.id)}
            disabled={disabled}
          />
        ))}
      </div>
    </div>
  );
}
