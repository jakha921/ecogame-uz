# ПРИЛОЖЕНИЕ А. ЛИСТИНГИ КЛЮЧЕВОГО КОДА

## А.1 QuizService.calculate_score

```python
# backend/apps/game/services.py
@staticmethod
def calculate_score(
    is_correct: bool,
    time_spent_ms: int,
    time_limit: int,
    current_streak: int,
) -> int:
    """
    current_streak = number of consecutive correct answers BEFORE this one.
    streak=0 or 1 → ×1.0, streak=2 → ×1.5, streak=3 → ×2.0, streak≥4 → ×3.0
    """
    if not is_correct:
        return 0
    streak = min(current_streak, 4)
    multiplier = QuizService.STREAK_MULTIPLIERS.get(
        streak, QuizService.STREAK_MAX_MULTIPLIER
    )
    time_limit_ms = time_limit * 1000
    time_ratio = max(0.0, 1.0 - time_spent_ms / time_limit_ms)
    time_factor = 1.0 + 0.5 * time_ratio
    return math.floor(QuizService.BASE_POINTS * multiplier * time_factor)
```

## А.2 QuizService.submit_answer

```python
# backend/apps/game/services.py
@staticmethod
def submit_answer(
    session: QuizSession,
    question_id: int,
    answer_id: int | None,
    time_spent_ms: int,
) -> dict:
    try:
        question = Question.objects.prefetch_related("answers").get(
            pk=question_id, is_active=True
        )
    except Question.DoesNotExist:
        raise ValueError(f"Question {question_id} not found")

    if QuizAnswer.objects.filter(session=session, question_id=question_id).exists():
        raise ValueError("Already answered this question")

    correct_answer = question.answers.filter(is_correct=True).first()

    selected: Answer | None = None
    is_correct = False
    if answer_id is not None:
        try:
            selected = Answer.objects.get(pk=answer_id, question=question)
            is_correct = selected.is_correct
        except Answer.DoesNotExist:
            pass

    streak_before = session.current_streak
    if is_correct:
        session.current_streak += 1
        session.max_streak = max(session.max_streak, session.current_streak)
    else:
        session.current_streak = 0

    points = QuizService.calculate_score(
        is_correct, time_spent_ms, question.time_limit, streak_before
    )

    if is_correct:
        session.score += points
        session.correct_count += 1

    streak_val = session.current_streak
    streak_mult = QuizService.STREAK_MULTIPLIERS.get(
        min(streak_val, 4), QuizService.STREAK_MAX_MULTIPLIER
    )

    QuizAnswer.objects.create(
        session=session,
        question=question,
        selected_answer=selected,
        is_correct=is_correct,
        time_spent_ms=time_spent_ms,
    )
    session.save(update_fields=["score", "correct_count", "current_streak", "max_streak"])

    is_game_over = session.mode == QuizMode.MARATHON and not is_correct

    return {
        "is_correct": is_correct,
        "correct_answer_id": correct_answer.id if correct_answer else None,
        "explanation_uz": question.explanation_uz,
        "points_earned": points,
        "streak": streak_val,
        "streak_multiplier": streak_mult,
        "time_bonus": max(0, points - QuizService.BASE_POINTS),
        "total_score": session.score,
        "is_game_over": is_game_over,
    }
```

## А.3 QuestionSerializer (DRF)

```python
# backend/apps/game/serializers.py
class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "text_uz", "order"]
        # ВАЖНО: is_correct намеренно исключён для anti-cheat

class QuestionSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "id",
            "text_uz",
            "category",
            "difficulty",
            "question_type",
            "image",
            "time_limit",
            "source",
            "answers",
        ]

    def get_answers(self, obj: Question) -> list:
        answers = list(obj.answers.all())
        random.shuffle(answers)
        return AnswerSerializer(answers, many=True).data
```

## А.4 quizStore.ts (Zustand)

```typescript
// frontend/src/stores/quizStore.ts
import { create } from "zustand";
import { quizApi } from "@/api/quiz";
import type {
  ActionCategory, AnswerResult, DailyChallenge,
  PlayerStats, Question, QuizMode, QuizResult, QuizSession,
} from "@/api/types";

interface QuizState {
  currentSession: QuizSession | null;
  questions: Question[];
  currentQuestionIndex: number;
  lastResult: AnswerResult | null;
  showExplanation: boolean;
  score: number;
  streak: number;
  correctCount: number;
  quizResult: QuizResult | null;
  playerStats: PlayerStats | null;
  dailyChallenge: DailyChallenge | null;
  isLoading: boolean;
  error: string | null;
}

export const useQuizStore = create<QuizState & QuizActions>((set, get) => ({
  ...initialState,

  startQuiz: async (mode, category) => {
    set({ isLoading: true, error: null });
    try {
      const response = await quizApi.startSession({ mode, category });
      const { questions, session_id, ...session } = response.data;
      set({
        currentSession: { ...session, id: session_id ?? session.id },
        questions: questions ?? [],
        currentQuestionIndex: 0,
        score: 0, streak: 0, correctCount: 0,
        lastResult: null, showExplanation: false,
        quizResult: null, isLoading: false,
      });
    } catch {
      set({ isLoading: false, error: "Viktorinani boshlashda xato yuz berdi" });
    }
  },

  submitAnswer: async (questionId, answerId, timeSpentMs) => {
    const { currentSession } = get();
    if (!currentSession) return null;
    try {
      const response = await quizApi.submitAnswer(currentSession.id, {
        question_id: questionId, answer_id: answerId, time_spent_ms: timeSpentMs,
      });
      const result = response.data;
      set((s) => ({
        lastResult: result, showExplanation: true,
        score: result.total_score, streak: result.streak,
        correctCount: result.is_correct ? s.correctCount + 1 : s.correctCount,
      }));
      return result;
    } catch {
      set({ error: "Javob yuborishda xato" });
      return null;
    }
  },

  endQuiz: async () => {
    const { currentSession } = get();
    if (!currentSession) return null;
    set({ isLoading: true });
    try {
      const response = await quizApi.endSession(currentSession.id);
      const result = response.data;
      set({ quizResult: result, isLoading: false });
      return result;
    } catch {
      set({ isLoading: false, error: "Viktorinani tugatishda xato" });
      return null;
    }
  },

  reset: () => set(initialState),
}));
```

## А.5 Timer.tsx (React SVG компонент)

```typescript
// frontend/src/components/quiz/Timer.tsx
import { useEffect, useRef, useState } from "react";

interface TimerProps {
  timeLimit: number;
  onTimeUp: () => void;
  active: boolean;
}

const RADIUS = 20;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

export function Timer({ timeLimit, onTimeUp, active }: TimerProps) {
  const [elapsed, setElapsed] = useState(0);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    setElapsed(0);
    if (!active) return;
    intervalRef.current = setInterval(() => {
      setElapsed((prev) => {
        const next = prev + 100;
        if (next >= timeLimit * 1000) {
          clearInterval(intervalRef.current!);
          onTimeUp();
          return timeLimit * 1000;
        }
        return next;
      });
    }, 100);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [active, timeLimit, onTimeUp]);

  const ratio = Math.max(0, 1 - elapsed / (timeLimit * 1000));
  const remaining = Math.ceil((timeLimit * 1000 - elapsed) / 1000);
  const offset = CIRCUMFERENCE * (1 - ratio);
  const color = ratio > 0.5 ? "#22c55e" : ratio > 0.2 ? "#eab308" : "#ef4444";

  return (
    <div className="relative flex items-center justify-center w-14 h-14">
      <svg width="56" height="56" viewBox="0 0 56 56" className="-rotate-90">
        <circle cx="28" cy="28" r={RADIUS} fill="none"
                stroke="#e5e7eb" strokeWidth="4" />
        <circle cx="28" cy="28" r={RADIUS} fill="none"
                stroke={color} strokeWidth="4"
                strokeDasharray={CIRCUMFERENCE}
                strokeDashoffset={offset}
                strokeLinecap="round"
                style={{ transition: "stroke-dashoffset 0.1s linear, stroke 0.3s" }}
        />
      </svg>
      <span className="absolute text-sm font-bold" style={{ color }}>
        {remaining}
      </span>
    </div>
  );
}
```
