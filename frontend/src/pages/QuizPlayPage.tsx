import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Loader2 } from "lucide-react";
import type { ActionCategory, QuizMode } from "@/api/types";
import {
  ExplanationPanel,
  QuestionCard,
  QuizHeader,
  StreakCounter,
  Timer,
} from "@/components/quiz";
import { useQuizStore } from "@/stores/quizStore";

type AnswerButtonState = "idle" | "selected" | "correct" | "incorrect";

interface QuizPlayPageProps {
  mode: QuizMode;
}

export function QuizPlayPage({ mode }: QuizPlayPageProps) {
  const { category } = useParams<{ category?: string }>();
  const navigate = useNavigate();

  const {
    currentSession,
    questions,
    currentQuestionIndex,
    lastResult,
    showExplanation,
    score,
    streak,
    isLoading,
    error,
    startQuiz,
    submitAnswer,
    nextQuestion,
    endQuiz,
  } = useQuizStore();

  const [answerState, setAnswerState] = useState<Record<number, AnswerButtonState>>({});
  const [timerKey, setTimerKey] = useState(0);
  // eslint-disable-next-line react-hooks/purity
  const startTimeRef = useRef<number>(Date.now());

  useEffect(() => {
    startQuiz(mode, category as ActionCategory | undefined);
  }, [mode, category, startQuiz]);

  // Reset per-question state on new question
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setAnswerState({});
    setTimerKey((k) => k + 1);
    startTimeRef.current = Date.now();
  }, [currentQuestionIndex]);

  const question = questions[currentQuestionIndex];
  const isLastQuestion = currentQuestionIndex >= questions.length - 1;

  const handleAnswer = useCallback(
    async (answerId: number | null) => {
      if (!question || showExplanation) return;
      const timeSpentMs = Date.now() - startTimeRef.current;

      if (answerId !== null) {
        setAnswerState((prev) => ({ ...prev, [answerId]: "selected" }));
      }

      const result = await submitAnswer(question.id, answerId, timeSpentMs);
      if (!result) return;

      // Update answer button states
      setAnswerState((prev) => {
        const next: Record<number, AnswerButtonState> = { ...prev };
        question.answers.forEach((a) => {
          if (a.id === result.correct_answer_id) {
            next[a.id] = "correct";
          } else if (prev[a.id] === "selected") {
            next[a.id] = "incorrect";
          }
        });
        return next;
      });

      if (result.is_game_over) {
        const quizResult = await endQuiz();
        if (quizResult?.session?.id) {
          navigate(`/quiz/results/${quizResult.session.id}`);
        } else {
          navigate("/");
        }
      }
    },
    [question, showExplanation, submitAnswer, endQuiz, navigate],
  );

  const handleNext = useCallback(async () => {
    if (isLastQuestion) {
      const result = await endQuiz();
      if (result?.session?.id) {
        navigate(`/quiz/results/${result.session.id}`);
      } else {
        navigate("/");
      }
    } else {
      nextQuestion();
    }
  }, [isLastQuestion, endQuiz, nextQuestion, navigate]);

  if (isLoading && !currentSession) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 size={32} className="animate-spin text-green-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center gap-4 min-h-[60vh] justify-center">
        <p className="text-red-500">{error}</p>
        <button onClick={() => navigate("/")} className="text-green-600 hover:underline">
          Bosh menyuga qaytish
        </button>
      </div>
    );
  }

  if (!question) return null;

  const streakMultiplier = streak <= 1 ? 1.0 : streak === 2 ? 1.5 : streak === 3 ? 2.0 : 3.0;

  return (
    <div className="max-w-2xl mx-auto flex flex-col gap-5">
      <QuizHeader
        current={currentQuestionIndex + 1}
        total={questions.length}
        score={score}
        streak={streak}
        streakMultiplier={streakMultiplier}
      />

      <div className="flex items-center justify-between">
        <StreakCounter streak={streak} multiplier={streakMultiplier} />
        <div className="ml-auto">
          <Timer
            key={timerKey}
            timeLimit={question.time_limit}
            active={!showExplanation}
            onTimeUp={() => handleAnswer(null)}
          />
        </div>
      </div>

      <QuestionCard
        question={question}
        onAnswer={handleAnswer}
        answerState={answerState}
        disabled={showExplanation}
      />

      {showExplanation && lastResult && (
        <ExplanationPanel
          isCorrect={lastResult.is_correct}
          explanation={lastResult.explanation_uz}
          pointsEarned={lastResult.points_earned}
          onNext={handleNext}
        />
      )}
    </div>
  );
}
