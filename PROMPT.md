# EcoGame Quiz — Дипломный проект

> **Автор:** Рузибаев Жахонгир Дилмуратович (036-21 SMMr)
> **Тема:** Разработка экологической игры по охране окружающей среды (на узбекском языке)
> **Научные руководители:** Узакова М.А., Абидова Ш.Б.
> **Стек:** Django REST + React 19 + Docker + Coolify
> **Домен:** https://ecogame.fullfocus.dev
>
> **Команда запуска ralph-loop:**
> ```
> /ralph-loop:ralph-loop "Прочитай PROMPT.md (/Users/jakha/MyFiles/University/Diploma/PROMPT.md). Найди первую незавершённую задачу [ ]. Выполни её полностью — создай файлы, напиши код, запусти проверку (uv run python manage.py check для бэкенда, npm run build для фронтенда). Отметь [x] в PROMPT.md. Закоммить изменения. Повторяй до ALL PHASES COMPLETE." --max-iterations 70 --completion-promise "ALL PHASES COMPLETE" /compact /senior-qa /senior-backend /senior-frontend /frontend-design:frontend-design /server-advisor
> ```

---

## Контекст пивота

Проект переключается с изометрической sandbox-игры (Phaser.js) на **экологическую викторину** (quiz).

**Что переиспользуется (~60% кодбазы):**
- `accounts` app — Player, JWT, anonymous login, claim account
- `leaderboard` app — LeaderboardEntry, signals, top-50 API
- `education` app — EducationalContent (5 статей), EcoFact (15 фактов)
- Admin panel (django-unfold), Docker/deploy, Frontend layout, auth pages

**Что убираем:** Phaser.js, GamePage, ToolbarPanel, frontend/src/game/

---

## Phase 1: Backend — Quiz модели

### [x] 1.1 Добавить новые модели Quiz в game/models.py

**Что сделать:**
- Открыть `backend/apps/game/models.py`
- СОХРАНИТЬ существующие: `ActionCategory`, `Level`, `GameSession`, `GameProgress`, `Achievement`, `PlayerAchievement`, `ConditionType`
- УДАЛИТЬ классы: `EcoAction`, `ActionLog` (вместе с их __str__ и Meta)
- ДОБАВИТЬ новые TextChoices:
  ```python
  class QuestionType(models.TextChoices):
      MCQ = "MCQ", "Ko'p tanlovli"
      TRUE_FALSE = "TRUE_FALSE", "To'g'ri/Noto'g'ri"
      SCENARIO = "SCENARIO", "Senariy"

  class QuizMode(models.TextChoices):
      QUICK = "QUICK", "Tezkor o'yin"
      CATEGORY = "CATEGORY", "Kategoriya bo'yicha"
      DAILY = "DAILY", "Kunlik vazifa"
      MARATHON = "MARATHON", "Marafon"
  ```
- РАСШИРИТЬ `ConditionType`: добавить `QUIZ_COUNT = "QUIZ_COUNT", "Количество викторин"`, `STREAK = "STREAK", "Серия ответов"`, `DAILY_STREAK = "DAILY_STREAK", "Ежедневная серия"`, `CATEGORY_MASTER = "CATEGORY_MASTER", "Мастер категории"`
- ДОБАВИТЬ модели (все с verbose_name, Meta, __str__):
  ```
  Question: text_uz(500), category(ActionCategory), difficulty(1-3, validators),
            question_type(QuestionType), explanation_uz, image(ImageField, optional),
            time_limit(30), source(200, blank), related_article(FK EducationalContent, null, blank),
            is_active(True), created_at(auto_now_add)

  Answer: question(FK CASCADE, related_name="answers"), text_uz(300), is_correct, order
          Meta: ordering = ["order"]

  QuizSession: player(FK AUTH_USER, CASCADE, related_name="quiz_sessions"), mode(QuizMode),
               category(ActionCategory, null, blank), started_at(auto_now_add),
               finished_at(null, blank), score(0), correct_count(0), total_questions(0),
               max_streak(0), current_streak(0)
               Meta: ordering = ["-started_at"]

  QuizAnswer: session(FK QuizSession, CASCADE, related_name="given_answers"),
              question(FK Question, CASCADE), selected_answer(FK Answer, SET_NULL, null, blank),
              is_correct, time_spent_ms, answered_at(auto_now_add)
              Meta: unique_together = ("session", "question")

  DailyChallenge: date(DateField, unique), questions(M2M Question, related_name="daily_challenges"),
                  bonus_score(50)

  MiniGameScore: player(FK AUTH_USER, CASCADE, related_name="mini_game_scores"),
                 game_type("SORTING", default), score, correct_count, total_items,
                 played_at(auto_now_add)
  ```
- Добавить импорт: `from django.core.validators import MinValueValidator, MaxValueValidator`

**Проверка:** `cd backend && uv run python manage.py check`
**Коммит:** `feat: Phase 1 — добавить Quiz модели (Question, Answer, QuizSession, QuizAnswer, DailyChallenge)`

---

### [x] 1.2 Создать миграции и обновить admin.py

**Что сделать:**
- Запустить `cd backend && uv run python manage.py makemigrations game --name quiz_models`
- Запустить `uv run python manage.py migrate`
- Открыть `backend/apps/game/admin.py`
- УДАЛИТЬ регистрации: EcoAction, ActionLog (если есть)
- ДОБАВИТЬ:
  ```python
  from unfold.admin import ModelAdmin, TabularInline
  from .models import (Question, Answer, QuizSession, QuizAnswer,
                       DailyChallenge, MiniGameScore, Achievement, PlayerAchievement)

  class AnswerInline(TabularInline):
      model = Answer
      extra = 4
      fields = ["text_uz", "is_correct", "order"]

  @admin.register(Question)
  class QuestionAdmin(ModelAdmin):
      list_display = ["text_uz_short", "category", "difficulty", "question_type", "is_active", "created_at"]
      list_filter = ["category", "difficulty", "question_type", "is_active"]
      search_fields = ["text_uz", "explanation_uz"]
      list_editable = ["is_active"]
      inlines = [AnswerInline]
      def text_uz_short(self, obj): return obj.text_uz[:60] + "..." if len(obj.text_uz) > 60 else obj.text_uz
      text_uz_short.short_description = "Savol"

  @admin.register(QuizSession)
  class QuizSessionAdmin(ModelAdmin):
      list_display = ["player", "mode", "category", "score", "correct_count", "total_questions", "started_at", "finished_at"]
      list_filter = ["mode", "category"]
      date_hierarchy = "started_at"
      readonly_fields = ["player", "started_at"]

  @admin.register(DailyChallenge)
  class DailyChallengeAdmin(ModelAdmin):
      list_display = ["date", "bonus_score", "question_count"]
      filter_horizontal = ["questions"]
      def question_count(self, obj): return obj.questions.count()
      question_count.short_description = "Savollar soni"

  @admin.register(MiniGameScore)
  class MiniGameScoreAdmin(ModelAdmin):
      list_display = ["player", "game_type", "score", "correct_count", "total_items", "played_at"]
  ```
- Сохранить регистрации Achievement и PlayerAchievement если были

**Проверка:** `uv run python manage.py check`, открыть `http://localhost:8000/admin/` — видны новые модели
**Коммит:** `feat: Phase 1 — миграции и admin для Quiz моделей`

---

## Phase 2: Backend — QuizService

### [ ] 2.1 Реализовать QuizService в services.py

**Что сделать:**
- Полностью заменить `backend/apps/game/services.py` новым QuizService
- Реализовать все методы:

```python
import math
import random
from datetime import date
from typing import Any

from django.db.models import Count, Q, Sum
from django.conf import settings

from .models import (
    Achievement, ActionCategory, Answer, ConditionType,
    DailyChallenge, PlayerAchievement, Question, QuizAnswer,
    QuizMode, QuizSession
)


class QuizService:
    BASE_POINTS = 100
    STREAK_MULTIPLIERS = {0: 1.0, 1: 1.0, 2: 1.5, 3: 2.0}
    STREAK_MAX_MULTIPLIER = 3.0
    MARATHON_MAX_QUESTIONS = 100
    RANK_TITLES = [
        (5000, "Eko-ustoz"),
        (3000, "Eko-qahramon"),
        (1500, "Eko-mutaxassis"),
        (500, "Tabiat do'sti"),
        (100, "Ekologik talaba"),
        (0, "Yangi o'quvchi"),
    ]

    @staticmethod
    def get_rank_title(total_score: int) -> str:
        for threshold, title in QuizService.RANK_TITLES:
            if total_score >= threshold:
                return title
        return "Yangi o'quvchi"

    @staticmethod
    def calculate_score(is_correct: bool, time_spent_ms: int, time_limit: int, current_streak: int) -> int:
        if not is_correct:
            return 0
        streak = min(current_streak, 4)
        multiplier = QuizService.STREAK_MULTIPLIERS.get(streak, QuizService.STREAK_MAX_MULTIPLIER)
        time_limit_ms = time_limit * 1000
        time_ratio = max(0.0, 1.0 - time_spent_ms / time_limit_ms)
        time_factor = 1.0 + 0.5 * time_ratio
        return math.floor(QuizService.BASE_POINTS * multiplier * time_factor)

    @staticmethod
    def get_questions_for_mode(mode: str, category: str | None, count: int = 10) -> list:
        qs = Question.objects.filter(is_active=True).prefetch_related("answers")
        if mode == QuizMode.CATEGORY and category:
            qs = qs.filter(category=category)
        elif mode == QuizMode.MARATHON:
            pass  # all questions
        questions = list(qs)
        random.shuffle(questions)
        if mode in [QuizMode.QUICK, QuizMode.DAILY]:
            questions = questions[:count]
        elif mode == QuizMode.MARATHON:
            questions = questions[:QuizService.MARATHON_MAX_QUESTIONS]
        return questions

    @staticmethod
    def start_session(player, mode: str, category: str | None = None) -> tuple:
        """Returns (QuizSession, list[Question])"""
        if mode == QuizMode.DAILY:
            daily = QuizService.get_daily_challenge()
            questions = list(daily.questions.filter(is_active=True).prefetch_related("answers"))
            random.shuffle(questions)
        else:
            questions = QuizService.get_questions_for_mode(mode, category)

        session = QuizSession.objects.create(
            player=player,
            mode=mode,
            category=category,
            total_questions=len(questions),
        )
        return session, questions

    @staticmethod
    def submit_answer(session: QuizSession, question_id: int, answer_id: int | None, time_spent_ms: int) -> dict:
        try:
            question = Question.objects.prefetch_related("answers").get(pk=question_id, is_active=True)
        except Question.DoesNotExist:
            raise ValueError(f"Question {question_id} not found")

        # Check duplicate
        if QuizAnswer.objects.filter(session=session, question_id=question_id).exists():
            raise ValueError("Already answered this question")

        correct_answer = question.answers.filter(is_correct=True).first()
        is_correct = False

        if answer_id is not None:
            try:
                selected = Answer.objects.get(pk=answer_id, question=question)
                is_correct = selected.is_correct
            except Answer.DoesNotExist:
                selected = None
        else:
            selected = None  # timeout

        # Update streak
        if is_correct:
            session.current_streak += 1
            session.max_streak = max(session.max_streak, session.current_streak)
        else:
            session.current_streak = 0

        points = QuizService.calculate_score(is_correct, time_spent_ms, question.time_limit, session.current_streak - 1 if is_correct else 0)

        if is_correct:
            session.score += points
            session.correct_count += 1

        streak_val = session.current_streak
        streak_mult = QuizService.STREAK_MULTIPLIERS.get(min(streak_val, 4), QuizService.STREAK_MAX_MULTIPLIER)

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

    @staticmethod
    def end_session(session: QuizSession) -> dict:
        from django.utils import timezone
        session.finished_at = timezone.now()
        session.save(update_fields=["finished_at"])

        accuracy = session.correct_count / session.total_questions if session.total_questions > 0 else 0.0

        # Update player total_score
        player = session.player
        total = QuizSession.objects.filter(
            player=player, finished_at__isnull=False
        ).aggregate(t=Sum("score"))["t"] or 0
        player.__class__.objects.filter(pk=player.pk).update(total_score=total)

        achievements = QuizService.check_quiz_achievements(player, session)

        return {
            "session": session,
            "accuracy": round(accuracy, 3),
            "rank_title": QuizService.get_rank_title(total),
            "achievements_unlocked": achievements,
        }

    @staticmethod
    def get_daily_challenge(target_date=None) -> DailyChallenge:
        if target_date is None:
            target_date = date.today()
        challenge, created = DailyChallenge.objects.get_or_create(
            date=target_date,
            defaults={"bonus_score": 50}
        )
        if created:
            questions = list(Question.objects.filter(is_active=True).order_by("?")[:10])
            challenge.questions.set(questions)
        return challenge

    @staticmethod
    def get_player_stats(player) -> dict:
        sessions = QuizSession.objects.filter(player=player, finished_at__isnull=False)
        total_quizzes = sessions.count()
        total_correct = sessions.aggregate(t=Sum("correct_count"))["t"] or 0
        total_questions = sessions.aggregate(t=Sum("total_questions"))["t"] or 0
        best_streak = sessions.aggregate(m=models_max("max_streak"))["m"] or 0
        accuracy = total_correct / total_questions if total_questions > 0 else 0.0

        per_category = {}
        for cat in ActionCategory.values:
            cat_sessions = sessions.filter(category=cat)
            cat_correct = cat_sessions.aggregate(t=Sum("correct_count"))["t"] or 0
            cat_total = cat_sessions.aggregate(t=Sum("total_questions"))["t"] or 0
            per_category[cat] = {
                "total": cat_total,
                "correct": cat_correct,
                "accuracy": round(cat_correct / cat_total, 3) if cat_total else 0.0,
            }

        return {
            "total_quizzes": total_quizzes,
            "total_correct": total_correct,
            "accuracy_pct": round(accuracy * 100, 1),
            "best_streak": best_streak,
            "daily_streak": 0,  # TODO: calculate consecutive days
            "rank_title": QuizService.get_rank_title(player.total_score),
            "per_category": per_category,
        }

    @staticmethod
    def check_quiz_achievements(player, session: QuizSession) -> list:
        all_achievements = Achievement.objects.all()
        earned = set(PlayerAchievement.objects.filter(player=player).values_list("achievement_id", flat=True))
        new_achievements = []

        total_quizzes = QuizSession.objects.filter(player=player, finished_at__isnull=False).count()

        for ach in all_achievements:
            if ach.id in earned:
                continue
            unlocked = False
            cv = ach.condition_value

            if ach.condition_type == ConditionType.SCORE:
                unlocked = player.total_score >= cv.get("min_score", 0)
            elif ach.condition_type == ConditionType.QUIZ_COUNT:
                unlocked = total_quizzes >= cv.get("count", 1)
            elif ach.condition_type == ConditionType.STREAK:
                unlocked = session.max_streak >= cv.get("min_streak", 5)
            elif ach.condition_type == ConditionType.LEVEL_COMPLETE:
                pass  # skip level-based for now

            if unlocked:
                pa = PlayerAchievement.objects.create(player=player, achievement=ach)
                new_achievements.append(ach)
                earned.add(ach.id)

        return new_achievements
```

- Добавить `from django.db.models import Max as models_max` в импорты

**Проверка:** `uv run python manage.py check`
**Коммит:** `feat: Phase 2 — QuizService (scoring, streak, daily challenge, achievements)`

---

## Phase 3: Backend — Quiz API

### [ ] 3.1 Создать сериализаторы для квиза

**Что сделать:**
- Открыть `backend/apps/game/serializers.py`
- УДАЛИТЬ: EcoActionSerializer, ActionLogSerializer, GameSessionSerializer если есть
- СОХРАНИТЬ: AchievementSerializer, PlayerAchievementSerializer (если есть)
- ДОБАВИТЬ все новые сериализаторы:

```python
from rest_framework import serializers
from .models import (Answer, Question, QuizSession, QuizAnswer,
                     DailyChallenge, Achievement, PlayerAchievement, MiniGameScore)


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "text_uz", "order"]  # НЕ включать is_correct


class AnswerWithCorrectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "text_uz", "order", "is_correct"]


class QuestionSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ["id", "text_uz", "category", "difficulty", "question_type",
                  "image", "time_limit", "source", "answers"]

    def get_answers(self, obj):
        answers = list(obj.answers.all())
        random.shuffle(answers)
        return AnswerSerializer(answers, many=True).data


class QuizSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizSession
        fields = ["id", "mode", "category", "started_at", "finished_at",
                  "score", "correct_count", "total_questions", "max_streak"]


class QuizSessionCreateSerializer(serializers.Serializer):
    mode = serializers.ChoiceField(choices=QuizMode.choices)
    category = serializers.ChoiceField(choices=ActionCategory.choices, required=False, allow_null=True)

    def validate(self, data):
        if data["mode"] == "CATEGORY" and not data.get("category"):
            raise serializers.ValidationError({"category": "Category mode requires a category."})
        return data


class SubmitAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer_id = serializers.IntegerField(required=False, allow_null=True)
    time_spent_ms = serializers.IntegerField(min_value=0, max_value=120000)


class DailyChallengeSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = DailyChallenge
        fields = ["id", "date", "questions", "bonus_score", "is_completed"]

    def get_is_completed(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return QuizSession.objects.filter(
            player=request.user,
            mode="DAILY",
            started_at__date=obj.date,
            finished_at__isnull=False,
        ).exists()


class MiniGameScoreSerializer(serializers.Serializer):
    score = serializers.IntegerField(min_value=0)
    correct_count = serializers.IntegerField(min_value=0)
    total_items = serializers.IntegerField(min_value=1)


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ["id", "key", "name_uz", "description_uz", "icon"]


class PlayerAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)

    class Meta:
        model = PlayerAchievement
        fields = ["id", "achievement", "unlocked_at"]
```

- Добавить `import random` в начало файла
- Добавить `from .models import QuizMode, ActionCategory`

**Проверка:** `uv run python manage.py check`
**Коммит:** `feat: Phase 3 — Quiz сериализаторы`

---

### [ ] 3.2 Создать Quiz views и обновить URL

**Что сделать:**
- Открыть `backend/apps/game/views.py`
- УДАЛИТЬ: LevelViewSet, EcoActionListView, SessionStartView, SessionEndView, ActionSubmitView, GameProgressListView если есть (они ссылаются на удалённые модели)
- СОХРАНИТЬ: AchievementListView, PlayerAchievementListView
- ДОБАВИТЬ новые views:

```python
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Question, QuizSession, DailyChallenge, MiniGameScore, ActionCategory
from .serializers import (
    QuestionSerializer, QuizSessionSerializer, QuizSessionCreateSerializer,
    SubmitAnswerSerializer, DailyChallengeSerializer, MiniGameScoreSerializer,
    AchievementSerializer, PlayerAchievementSerializer
)
from .services import QuizService


class QuestionListView(generics.ListAPIView):
    """GET /api/v1/game/quiz/questions/?category=X&difficulty=N&limit=10"""
    serializer_class = QuestionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Question.objects.filter(is_active=True).prefetch_related("answers")
        category = self.request.query_params.get("category")
        difficulty = self.request.query_params.get("difficulty")
        if category in ActionCategory.values:
            qs = qs.filter(category=category)
        if difficulty and difficulty.isdigit():
            qs = qs.filter(difficulty=int(difficulty))
        return qs.order_by("?")[:int(self.request.query_params.get("limit", 20))]


class QuizSessionStartView(APIView):
    """POST /api/v1/game/quiz/sessions/ {mode, category?}"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = QuizSessionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session, questions = QuizService.start_session(
            player=request.user,
            mode=serializer.validated_data["mode"],
            category=serializer.validated_data.get("category"),
        )
        session_data = QuizSessionSerializer(session).data
        session_data["questions"] = QuestionSerializer(questions, many=True).data
        return Response(session_data, status=status.HTTP_201_CREATED)


class QuizAnswerSubmitView(APIView):
    """POST /api/v1/game/quiz/sessions/{session_id}/answer/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, session_id):
        try:
            session = QuizSession.objects.get(pk=session_id, player=request.user, finished_at__isnull=True)
        except QuizSession.DoesNotExist:
            return Response({"detail": "Session not found or already finished."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubmitAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = QuizService.submit_answer(
                session=session,
                question_id=serializer.validated_data["question_id"],
                answer_id=serializer.validated_data.get("answer_id"),
                time_spent_ms=serializer.validated_data["time_spent_ms"],
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result)


class QuizSessionEndView(APIView):
    """POST /api/v1/game/quiz/sessions/{session_id}/end/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, session_id):
        try:
            session = QuizSession.objects.get(pk=session_id, player=request.user, finished_at__isnull=True)
        except QuizSession.DoesNotExist:
            return Response({"detail": "Session not found."}, status=status.HTTP_404_NOT_FOUND)

        result = QuizService.end_session(session)
        return Response({
            "session": QuizSessionSerializer(result["session"]).data,
            "accuracy": result["accuracy"],
            "rank_title": result["rank_title"],
            "achievements_unlocked": AchievementSerializer(result["achievements_unlocked"], many=True).data,
        })


class DailyChallengeView(APIView):
    """GET /api/v1/game/quiz/daily/"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        challenge = QuizService.get_daily_challenge()
        return Response(DailyChallengeSerializer(challenge, context={"request": request}).data)


class PlayerStatsView(APIView):
    """GET /api/v1/game/quiz/stats/"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        stats = QuizService.get_player_stats(request.user)
        return Response(stats)


class MiniGameScoreView(APIView):
    """POST /api/v1/game/mini-game/sort/score/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = MiniGameScoreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        score_obj = MiniGameScore.objects.create(
            player=request.user,
            game_type="SORTING",
            **serializer.validated_data,
        )
        # Добавить к total_score игрока
        request.user.__class__.objects.filter(pk=request.user.pk).update(
            total_score=request.user.__class__.objects.get(pk=request.user.pk).total_score + score_obj.score
        )
        return Response({"score": score_obj.score, "message": "Natija saqlandi!"}, status=status.HTTP_201_CREATED)


class AchievementListView(generics.ListAPIView):
    serializer_class = AchievementSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Achievement.objects.all().order_by("condition_type", "key")
    pagination_class = None


class PlayerAchievementListView(generics.ListAPIView):
    serializer_class = PlayerAchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return PlayerAchievement.objects.filter(
            player=self.request.user
        ).select_related("achievement").order_by("-unlocked_at")
```

- Открыть `backend/apps/game/urls.py` и ЗАМЕНИТЬ:
```python
from django.urls import path
from . import views

urlpatterns = [
    # Quiz
    path("quiz/questions/", views.QuestionListView.as_view(), name="quiz-questions"),
    path("quiz/sessions/", views.QuizSessionStartView.as_view(), name="quiz-session-start"),
    path("quiz/sessions/<int:session_id>/answer/", views.QuizAnswerSubmitView.as_view(), name="quiz-answer"),
    path("quiz/sessions/<int:session_id>/end/", views.QuizSessionEndView.as_view(), name="quiz-session-end"),
    path("quiz/daily/", views.DailyChallengeView.as_view(), name="quiz-daily"),
    path("quiz/stats/", views.PlayerStatsView.as_view(), name="quiz-stats"),
    # Mini-game
    path("mini-game/sort/score/", views.MiniGameScoreView.as_view(), name="mini-game-sort"),
    # Achievements
    path("achievements/", views.AchievementListView.as_view(), name="achievements"),
    path("achievements/my/", views.PlayerAchievementListView.as_view(), name="my-achievements"),
]
```

**Проверка:** `uv run python manage.py check`
**Коммит:** `feat: Phase 3 — Quiz API endpoints (questions, sessions, answer, daily, stats)`

---

## Phase 4: Backend — Signals и Leaderboard

### [ ] 4.1 Обновить leaderboard signals для QuizSession

**Что сделать:**
- Открыть `backend/apps/leaderboard/signals.py`
- УДАЛИТЬ/ЗАМЕНИТЬ сигнал для GameProgress (заменить на QuizSession)
- ДОБАВИТЬ:
```python
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.game.models import PlayerAchievement, QuizSession
from apps.accounts.models import Player
from .models import LeaderboardEntry


@receiver(post_save, sender=QuizSession)
def update_leaderboard_on_quiz(sender, instance: QuizSession, **kwargs):
    """Обновить лидерборд при завершении квиза."""
    if instance.finished_at is None:
        return  # только для завершённых сессий

    player = instance.player
    # Пересчитать total_score из всех завершённых сессий
    quiz_total = QuizSession.objects.filter(
        player=player, finished_at__isnull=False
    ).aggregate(total=Sum("score"))["total"] or 0

    # Обновить поле игрока
    Player.objects.filter(pk=player.pk).update(total_score=quiz_total)

    # Обновить LeaderboardEntry
    quizzes_count = QuizSession.objects.filter(player=player, finished_at__isnull=False).count()
    achievement_count = PlayerAchievement.objects.filter(player=player).count()

    entry, _ = LeaderboardEntry.objects.get_or_create(player=player)
    entry.total_score = quiz_total
    entry.levels_completed = quizzes_count  # repurposed: теперь хранит количество квизов
    entry.achievements_count = achievement_count
    entry.save(update_fields=["total_score", "levels_completed", "achievements_count", "updated_at"])

    # Пересчитать ранги
    for rank, e in enumerate(LeaderboardEntry.objects.order_by("-total_score"), start=1):
        if e.rank != rank:
            LeaderboardEntry.objects.filter(pk=e.pk).update(rank=rank)


@receiver(post_save, sender=PlayerAchievement)
def update_leaderboard_on_achievement(sender, instance: PlayerAchievement, **kwargs):
    """Обновить счётчик достижений."""
    count = PlayerAchievement.objects.filter(player=instance.player).count()
    LeaderboardEntry.objects.filter(player=instance.player).update(achievements_count=count)
```

**Проверка:** `uv run python manage.py check`
**Коммит:** `feat: Phase 4 — leaderboard signal для QuizSession`

---

## Phase 5: Backend — Фикстуры (150 вопросов)

### [ ] 5.1 Создать fixtures/questions.json

**Что сделать:**
- Создать файл `backend/fixtures/questions.json`
- 150 вопросов: по 30 на каждую категорию (FLORA, WATER, WASTE, ENERGY, FAUNA)
- Формат Django fixture, pk = 1..150
- Каждый вопрос — запись Question + 2-4 записи Answer
- Answer pk начинается с 1001 (чтобы не конфликтовать)
- Примерная структура:
```json
[
  {
    "model": "game.question",
    "pk": 1,
    "fields": {
      "text_uz": "O'zbekistonda bir yilda o'rtacha necha kun quyoshli bo'ladi?",
      "category": "ENERGY",
      "difficulty": 1,
      "question_type": "MCQ",
      "explanation_uz": "O'zbekiston quyoshli kunlar soni bo'yicha dunyoda yetakchi o'rinlardan birini egallaydi. Bu quyosh energiyasini keng qo'llash imkonini beradi.",
      "image": "",
      "time_limit": 30,
      "source": "O'zbekiston Quyosh energiyasi instituti",
      "related_article": null,
      "is_active": true
    }
  },
  {
    "model": "game.answer",
    "pk": 1001,
    "fields": {"question": 1, "text_uz": "150 kun", "is_correct": false, "order": 1}
  },
  {
    "model": "game.answer",
    "pk": 1002,
    "fields": {"question": 1, "text_uz": "200 kun", "is_correct": false, "order": 2}
  },
  {
    "model": "game.answer",
    "pk": 1003,
    "fields": {"question": 1, "text_uz": "300 kun", "is_correct": true, "order": 3}
  },
  {
    "model": "game.answer",
    "pk": 1004,
    "fields": {"question": 1, "text_uz": "350 kun", "is_correct": false, "order": 4}
  }
]
```

- Написать 150 вопросов в узбекском языке (латиница) по темам:
  - ENERGY (pk 1-30): quyosh energiyasi, LED, energiya tejash, CO2, elektr, vetro, bio-gaz
  - WATER (pk 31-60): Orol dengizi, Amudaryo, Sirdaryo, suv tejash, ifloslanish, qayta ishlatish
  - FLORA (pk 61-90): daraxt, o'rmon, o'simlik, fotosintez, CO2 yutish, ekish
  - WASTE (pk 91-120): plastik, shisha, qog'oz, batareya, elektron, decomposition, qayta ishlash
  - FAUNA (pk 121-150): Qizil kitob, jayron, qunduz, qushlar, baliq, tabiat qo'riqxonalari

- Каждый вопрос должен содержать реальный образовательный факт об экологии Узбекистана

**Проверка:** `uv run python manage.py loaddata fixtures/questions.json`
**Коммит:** `feat: Phase 5 — 150 quiz вопросов на узбекском языке`

---

### [ ] 5.2 Создать fixtures/quiz_achievements.json

**Что сделать:**
- Создать `backend/fixtures/quiz_achievements.json` с 10 достижениями:
```json
[
  {"model": "game.achievement", "pk": 1, "fields": {"key": "first_quiz", "name_uz": "Birinchi viktorina", "description_uz": "Birinchi viktorinani tugatdingiz!", "icon": "star", "condition_type": "QUIZ_COUNT", "condition_value": {"count": 1}}},
  {"model": "game.achievement", "pk": 2, "fields": {"key": "quiz_veteran", "name_uz": "Viktorina ishqibozi", "description_uz": "10 ta viktorinani tugatdingiz", "icon": "trophy", "condition_type": "QUIZ_COUNT", "condition_value": {"count": 10}}},
  {"model": "game.achievement", "pk": 3, "fields": {"key": "perfect_score", "name_uz": "Mukammal natija", "description_uz": "Viktorinada barcha savollarga to'g'ri javob berdingiz", "icon": "crown", "condition_type": "SCORE", "condition_value": {"min_score": 1000}}},
  {"model": "game.achievement", "pk": 4, "fields": {"key": "streak_5", "name_uz": "5 ta ketma-ket", "description_uz": "5 ta savolga ketma-ket to'g'ri javob berdingiz", "icon": "fire", "condition_type": "STREAK", "condition_value": {"min_streak": 5}}},
  {"model": "game.achievement", "pk": 5, "fields": {"key": "streak_10", "name_uz": "O'n ketma-ket", "description_uz": "10 ta savolga ketma-ket to'g'ri javob berdingiz", "icon": "bolt", "condition_type": "STREAK", "condition_value": {"min_streak": 10}}},
  {"model": "game.achievement", "pk": 6, "fields": {"key": "eco_expert", "name_uz": "Eko-mutaxassis", "description_uz": "1500 ball to'pladingiz", "icon": "leaf", "condition_type": "SCORE", "condition_value": {"min_score": 1500}}},
  {"model": "game.achievement", "pk": 7, "fields": {"key": "eco_master", "name_uz": "Eko-ustoz", "description_uz": "5000 ball to'pladingiz", "icon": "crown", "condition_type": "SCORE", "condition_value": {"min_score": 5000}}},
  {"model": "game.achievement", "pk": 8, "fields": {"key": "water_lover", "name_uz": "Suv himoyachisi", "description_uz": "Suv bo'yicha 20 ta viktorina o'tdingiz", "icon": "water", "condition_type": "QUIZ_COUNT", "condition_value": {"count": 20}}},
  {"model": "game.achievement", "pk": 9, "fields": {"key": "nature_friend", "name_uz": "Tabiat do'sti", "description_uz": "500 ball to'pladingiz", "icon": "tree", "condition_type": "SCORE", "condition_value": {"min_score": 500}}},
  {"model": "game.achievement", "pk": 10, "fields": {"key": "marathon_hero", "name_uz": "Marafon qahramoni", "description_uz": "Marafon rejimida 20 ta savolga to'g'ri javob berdingiz", "icon": "star", "condition_type": "STREAK", "condition_value": {"min_streak": 20}}}
]
```

**Проверка:** `uv run python manage.py loaddata fixtures/quiz_achievements.json`
**Коммит:** `feat: Phase 5 — quiz achievements fixture (10 достижений)`

---

## Phase 6: Backend — Тесты

### [ ] 6.1 Написать тесты для Quiz моделей и сервиса

**Что сделать:**
- Обновить `backend/apps/game/tests/test_models.py` — убрать тесты для EcoAction/ActionLog, добавить:
  - TestQuestionModel: create, defaults, difficulty validation, active filter
  - TestAnswerModel: ordering, FK cascade, is_correct
  - TestQuizSessionModel: create quick/marathon/daily, default values
  - TestQuizAnswerModel: unique_together constraint
  - TestDailyChallengeModel: date unique
- Обновить `backend/apps/game/tests/test_services.py` — убрать ecosystem тесты, добавить:
  - TestCalculateScore: correct with streak 1/2/3/4, incorrect=0, time bonus
  - TestStartSession: quick mode 10 questions, category mode filters, marathon <= 100
  - TestSubmitAnswer: correct increases streak, wrong resets, marathon game_over
  - TestEndSession: sets finished_at, calculates accuracy, updates player.total_score
  - TestDailyChallenge: auto-creates, returns same for same date
  - TestGetRankTitle: boundary values (0, 99, 100, 499, 500, ...)
  - TestCheckAchievements: SCORE threshold, QUIZ_COUNT threshold, STREAK threshold
- Обновить `backend/apps/game/tests/test_api.py` — убрать sandbox тесты, добавить:
  - TestQuizSessionAPI: start, unauthorized, invalid mode
  - TestSubmitAnswerAPI: correct/incorrect, duplicate, wrong session
  - TestEndSessionAPI: returns results with accuracy
  - TestDailyChallengeAPI: get challenge, is_completed flag
  - TestPlayerStatsAPI: returns stats after quiz
  - TestFullQuizFlow: start → answer×10 → end → check score
- Обновить `backend/apps/leaderboard/tests/test_api.py`: добавить test для QuizSession signal

**Проверка:** `uv run pytest -v` — все тесты зелёные
**Коммит:** `test: Phase 6 — тесты для Quiz моделей, сервиса и API`

---

## Phase 7: Frontend — Убрать Phaser, Quiz Types & Store

### [ ] 7.1 Удалить Phaser, обновить types, создать quizStore

**Что сделать:**
- Удалить директорию: `frontend/src/game/` (все файлы)
- Удалить файлы: `frontend/src/pages/GamePage.tsx`, `frontend/src/components/game/ToolbarPanel.tsx`, `frontend/src/components/game/ToolButton.tsx`, `frontend/src/components/HealthBar.tsx`, `frontend/src/hooks/useGameSync.ts`
- В `frontend/package.json` — убрать `"phaser"` из dependencies
- Запустить `cd frontend && npm uninstall phaser`
- Полностью переписать `frontend/src/api/types.ts`:
  - УБРАТЬ: EcosystemState, MapZone, MapConfig, EcoAction, ActionItem, EcosystemConfig
  - ОСТАВИТЬ: Player, AuthTokens, RegisterData, LoginData, PaginatedResponse, ActionCategory, Achievement, PlayerAchievement, LeaderboardEntry, EducationalContent, EcoFact
  - ДОБАВИТЬ quiz types: QuestionType, QuizMode, Answer, Question, QuizSession, AnswerResult, QuizResult, PlayerStats, DailyChallenge, SortingItem
- Создать `frontend/src/api/quiz.ts`:
  ```typescript
  import { apiClient } from "./client";
  import type { ... } from "./types";

  export const quizApi = {
    getQuestions: (params?) => apiClient.get<PaginatedResponse<Question>>("/game/quiz/questions/", { params }),
    startSession: (data: { mode: QuizMode; category?: ActionCategory }) =>
      apiClient.post<QuizSession & { questions: Question[] }>("/game/quiz/sessions/", data),
    submitAnswer: (sessionId: number, data: { question_id: number; answer_id: number | null; time_spent_ms: number }) =>
      apiClient.post<AnswerResult>(`/game/quiz/sessions/${sessionId}/answer/`, data),
    endSession: (sessionId: number) =>
      apiClient.post<QuizResult>(`/game/quiz/sessions/${sessionId}/end/`),
    getDailyChallenge: () => apiClient.get<DailyChallenge>("/game/quiz/daily/"),
    getStats: () => apiClient.get<PlayerStats>("/game/quiz/stats/"),
    getAchievements: () => apiClient.get<PaginatedResponse<Achievement>>("/game/achievements/"),
    getMyAchievements: () => apiClient.get<PaginatedResponse<PlayerAchievement>>("/game/achievements/my/"),
    submitMiniGameScore: (data: { score: number; correct_count: number; total_items: number }) =>
      apiClient.post("/game/mini-game/sort/score/", data),
  };
  ```
- Создать `frontend/src/stores/quizStore.ts` с Zustand:
  - State: currentSession, questions, currentQuestionIndex, lastResult, showExplanation, score, streak, correctCount, quizResult, playerStats, dailyChallenge, isLoading
  - Actions: startQuiz, submitAnswer, nextQuestion, endQuiz, loadStats, loadDailyChallenge, reset
- Обновить `frontend/src/App.tsx`:
  - Убрать импорты GamePage
  - Добавить роуты: `/quiz/quick`, `/quiz/category/:category`, `/quiz/daily`, `/quiz/marathon`, `/quiz/results/:sessionId`, `/mini-game/sort`
  - Временно поставить заглушки для новых страниц (QuizPlayPage, QuizResultsPage, EcoSortingPage) — просто `<div>Coming soon</div>`

**Проверка:** `npm run build`
**Коммит:** `feat: Phase 7 — убрать Phaser, добавить quiz types/store/API`

---

## Phase 8: Frontend — Quiz UI компоненты

### [ ] 8.1 Создать компоненты для квиза

**Что сделать:**
- Создать директорию `frontend/src/components/quiz/`
- Создать файлы (все компоненты с TypeScript, Tailwind CSS, без emoji кроме иконок Lucide):

**`QuizHeader.tsx`** — прогресс-бар + счёт + стрик:
```tsx
interface QuizHeaderProps {
  current: number; total: number; score: number; streak: number; streakMultiplier: number;
}
// Показать: "Savol N / M" + прогресс-бар + "Jami: X ball" + streak badge если streak >= 2
```

**`Timer.tsx`** — круговой SVG таймер:
```tsx
interface TimerProps { timeLimit: number; onTimeUp: () => void; active: boolean; }
// SVG circle с stroke-dashoffset анимацией
// Цвет: зелёный > 50%, жёлтый > 20%, красный <= 20%
// useEffect с 100ms interval для плавности
```

**`AnswerButton.tsx`** — кнопка ответа:
```tsx
interface AnswerButtonProps {
  answer: Answer; state: "idle" | "selected" | "correct" | "incorrect";
  onClick: () => void; disabled: boolean;
}
// idle: белый border. selected: синий. correct: зелёный + CheckCircle. incorrect: красный + XCircle
```

**`QuestionCard.tsx`** — карточка вопроса:
```tsx
interface QuestionCardProps {
  question: Question; onAnswer: (answerId: number | null) => void;
  answerState: Record<number, "idle" | "selected" | "correct" | "incorrect">;
  disabled: boolean;
}
// Заголовок вопроса + grid 2 колонки AnswerButton
// TRUE_FALSE: 2 кнопки в ряд (Ha / Yo'q)
```

**`StreakCounter.tsx`** — бейдж стрика:
```tsx
interface StreakCounterProps { streak: number; multiplier: number; }
// Показывать только если streak >= 2
// 🔥 иконка (Flame из lucide) + "5 ketma-ket! ×2.0"
```

**`ExplanationPanel.tsx`** — пояснение после ответа:
```tsx
interface ExplanationPanelProps {
  isCorrect: boolean; explanation: string; pointsEarned: number;
  onNext: () => void; articleId?: number;
}
// Зелёный/красный banner + explanation text + "Maqolani o'qish" ссылка + "Keyingi" кнопка
```

**`CategorySelector.tsx`** — выбор категории:
```tsx
// Grid из 5 категорий с иконками (TreeDeciduous/Droplets/Recycle/SunMedium/Bird)
// onClick возвращает ActionCategory
```

**`ModeCard.tsx`** — карточка режима для главной:
```tsx
interface ModeCardProps {
  title: string; description: string; icon: React.ReactNode;
  color: string; onClick: () => void; badge?: string;
}
```

**Проверка:** `npm run build`
**Коммит:** `feat: Phase 8 — Quiz UI компоненты (Timer, QuestionCard, ExplanationPanel, ...)`

---

## Phase 9: Frontend — Quiz Pages

### [ ] 9.1 Создать QuizPlayPage и QuizResultsPage

**Что сделать:**
- Создать `frontend/src/pages/QuizPlayPage.tsx`:
  - Props: не нужны, читает mode из URL params / route state
  - useParams для category в category mode
  - useEffect: при монтировании вызвать `quizStore.startQuiz(mode, category)`
  - Флоу: loading → вопросы → [показать вопрос → ответ → 2-3 сек explanation → следующий] → results
  - Компоненты: QuizHeader + Timer + QuestionCard + ExplanationPanel
  - При завершении: navigate(`/quiz/results/${session.id}`)
  - Для Marathon: при `is_game_over=true` сразу завершить

- Создать `frontend/src/pages/QuizResultsPage.tsx`:
  - useParams: sessionId
  - Показать: итоговый счёт (крупно), accuracy (%), max_streak, rank_title
  - Список разблокированных достижений (если есть)
  - Кнопки: "Yana o'ynash" → /quiz/quick, "Bosh menyu" → /
  - Анимация появления (CSS transition)

- Полностью переписать `frontend/src/pages/MainMenu.tsx`:
  - Hero секция (зелёный градиент) с названием EcoGame
  - Сетка 2×2 карточек режимов: Quick Play, By Category, Daily Challenge, Marathon
  - Карточка мини-игры "Chiqindi saralash"
  - Статистика игрока (если авторизован): rank_title, total_score, daily streak
  - Daily eco-fact (оставить)
  - Ссылки: Education, Leaderboard

- Обновить `frontend/src/i18n/uz.json`:
  ```json
  "quiz": {
    "title": "Ekologik viktorina",
    "quick": "Tezkor o'yin",
    "quick_desc": "10 ta tasodifiy savol",
    "category": "Kategoriya bo'yicha",
    "category_desc": "Bir kategoriyadan barcha savollar",
    "daily": "Kunlik vazifa",
    "daily_desc": "Har kuni yangi savollar + bonus",
    "marathon": "Marafon",
    "marathon_desc": "Birinchi xatogacha o'ynang",
    "correct": "To'g'ri!",
    "wrong": "Noto'g'ri!",
    "time_up": "Vaqt tugadi!",
    "next_question": "Keyingi savol",
    "results": "Natijalar",
    "accuracy": "Aniqlik",
    "your_score": "Sizning ballingiz",
    "best_streak": "Eng uzun ketma-ketlik",
    "play_again": "Qayta o'ynash",
    "select_category": "Kategoriya tanlang"
  },
  "categories": {
    "FLORA": "O'simliklar",
    "WATER": "Suv",
    "WASTE": "Chiqindi",
    "ENERGY": "Energiya",
    "FAUNA": "Hayvonlar"
  },
  "mini_game": {
    "title": "Chiqindi saralash",
    "desc": "Chiqindilarni to'g'ri idishga joylashtiring",
    "recyclable": "Qayta ishlanadigan",
    "organic": "Organik",
    "landfill": "Poligon",
    "drag_hint": "Chiqindini ushlab, kerakli idishga tashlang",
    "correct": "To'g'ri!",
    "wrong": "Noto'g'ri idish!"
  }
  ```

**Проверка:** `npm run build`
**Коммит:** `feat: Phase 9 — QuizPlayPage, QuizResultsPage, новая MainMenu`

---

## Phase 10: Frontend — Eco-sorting мини-игра

### [ ] 10.1 Создать мини-игру сортировки отходов

**Что сделать:**
- Создать `frontend/src/data/sortingItems.ts`:
```typescript
export type BinType = "recyclable" | "organic" | "landfill";

export interface SortingItem {
  id: string;
  name_uz: string;
  emoji: string;  // здесь можно emoji т.к. это игровые иконки предметов
  correct_bin: BinType;
  points: number;
}

export const SORTING_ITEMS: SortingItem[] = [
  { id: "plastic_bottle", name_uz: "Plastik shisha", emoji: "🧴", correct_bin: "recyclable", points: 10 },
  { id: "glass_jar", name_uz: "Shisha banka", emoji: "🫙", correct_bin: "recyclable", points: 10 },
  { id: "paper", name_uz: "Qog'oz", emoji: "📄", correct_bin: "recyclable", points: 10 },
  { id: "cardboard", name_uz: "Karton quti", emoji: "📦", correct_bin: "recyclable", points: 10 },
  { id: "aluminum_can", name_uz: "Alyuminiy banka", emoji: "🥫", correct_bin: "recyclable", points: 10 },
  { id: "food_waste", name_uz: "Ovqat qoldiqlari", emoji: "🍌", correct_bin: "organic", points: 10 },
  { id: "leaves", name_uz: "Barglar", emoji: "🍂", correct_bin: "organic", points: 10 },
  { id: "eggshell", name_uz: "Tuxum po'chog'i", emoji: "🥚", correct_bin: "organic", points: 10 },
  { id: "coffee_grounds", name_uz: "Qahva qoldig'i", emoji: "☕", correct_bin: "organic", points: 10 },
  { id: "flower", name_uz: "Gul", emoji: "🌻", correct_bin: "organic", points: 10 },
  { id: "battery", name_uz: "Batareya", emoji: "🔋", correct_bin: "landfill", points: 15 },
  { id: "phone", name_uz: "Eski telefon", emoji: "📱", correct_bin: "landfill", points: 15 },
  { id: "diaper", name_uz: "Bir martalik taomil", emoji: "🧷", correct_bin: "landfill", points: 10 },
  { id: "chip_bag", name_uz: "Chips paketi", emoji: "🛍️", correct_bin: "landfill", points: 10 },
  { id: "styrofoam", name_uz: "Styrofoam", emoji: "📦", correct_bin: "landfill", points: 10 },
  { id: "metal_can", name_uz: "Metal quti", emoji: "🥫", correct_bin: "recyclable", points: 10 },
  { id: "newspaper", name_uz: "Gazeta", emoji: "📰", correct_bin: "recyclable", points: 10 },
  { id: "fruit_peel", name_uz: "Meva po'chog'i", emoji: "🍊", correct_bin: "organic", points: 10 },
  { id: "light_bulb", name_uz: "Chiroq (energiyatejamkor)", emoji: "💡", correct_bin: "landfill", points: 15 },
  { id: "wire", name_uz: "Sim", emoji: "🔌", correct_bin: "landfill", points: 15 },
];
```

- Создать `frontend/src/components/mini-game/WasteBin.tsx`:
  - Props: binType, label, color, onDrop, isHighlighted
  - HTML5 onDragOver + onDrop handlers
  - Визуал: большой контейнер с иконкой + label, highlight при drag over

- Создать `frontend/src/components/mini-game/WasteItem.tsx`:
  - Props: item, draggable
  - HTML5 draggable=true + onDragStart
  - Показывает emoji + name_uz

- Создать `frontend/src/components/mini-game/SortingGame.tsx`:
  - State: currentItemIndex, score, correctCount, phase ("playing" | "feedback" | "done")
  - Shuffle items при старте
  - Показывает текущий item + 3 bin'а
  - Обрабатывает drop: correct/incorrect flash, pause 1.5s, следующий item
  - Touch support: onTouchStart + три tap-target zone (для мобильных: кнопки под item)
  - Завершение при всех 20 items или 5 ошибках

- Создать `frontend/src/pages/EcoSortingPage.tsx`:
  - Импортирует SortingGame
  - При завершении: вызвать `quizApi.submitMiniGameScore(...)` + показать результат
  - Кнопки: "Yana o'ynash", "Bosh menyu"

- Добавить роут в `App.tsx`: `<Route path="/mini-game/sort" element={<ProtectedRoute><EcoSortingPage /></ProtectedRoute>} />`
- Добавить карточку мини-игры в MainMenu с ссылкой `/mini-game/sort`

**Проверка:** `npm run build`
**Коммит:** `feat: Phase 10 — Eco-sorting мини-игра (drag & drop, 20 предметов)`

---

## Phase 11: ВКР — Дипломная работа с нуля

### [ ] 11.1 Написать Введение

**Что сделать:**
- Полностью переписать `docs/vkr/introduction.md`
- Объём: 5-6 страниц (≈ 2500-3000 слов)
- Структура:
  ```
  ВВЕДЕНИЕ
  
  Актуальность темы (1-1.5 стр):
  - Экологические проблемы Узбекистана (Аральское море, загрязнение воздуха, воды)
  - Необходимость экологического образования молодёжи
  - Роль цифровых технологий и геймификации в образовании
  - Нехватка образовательных игр на узбекском языке

  Степень изученности проблемы (0.5 стр):
  - Краткий обзор мировых исследований геймификации в образовании
  - Ссылки на 3-4 научных источника
  
  Цель работы: разработать веб-приложение "Экологическая викторина" на узбекском языке
  
  Задачи (пронумерованный список 5-7 пунктов):
  1. Анализ существующих аналогов экологических образовательных игр
  2. Проектирование архитектуры системы
  3. Разработка базы данных вопросов на узбекском языке
  4. Реализация квиз-движка с системой очков и достижений
  5. Реализация мини-игры сортировки отходов
  6. Тестирование и публикация приложения
  
  Объект исследования: процесс экологического образования молодёжи
  Предмет исследования: программное обеспечение для геймифицированного экологического обучения
  
  Методы исследования: анализ литературы, прототипирование, тестирование
  
  Практическая значимость:
  - Первая экологическая викторина на узбекском языке
  - Открытый исходный код, возможность масштабирования
  
  Структура работы:
  - Глава 1: анализ предметной области
  - Глава 2: проектирование
  - Глава 3: реализация
  - Глава 4: тестирование
  ```
- Форматирование: Times New Roman 14pt, межстрочный 1.5, поля 30/10/20/20

**Проверка:** Файл существует, объём 2500+ слов
**Коммит:** `docs: ВКР — Введение (актуальность, цель, задачи)`

---

### [ ] 11.2 Написать Главу 1 — Аналитическая часть

**Что сделать:**
- Полностью переписать `docs/vkr/chapter1_analysis.md`
- Объём: 15-20 страниц (≈ 8000-10000 слов)
- Структура:
  ```
  ГЛАВА 1. АНАЛИЗ ПРЕДМЕТНОЙ ОБЛАСТИ
  
  1.1 Экологические проблемы Узбекистана (3-4 стр)
      - Катастрофа Аральского моря (исторический контекст, последствия)
      - Загрязнение воздуха в Ташкенте и промышленных регионах
      - Деградация почв и опустынивание
      - Проблема бытовых отходов и переработки
      - Сокращение биоразнообразия (Красная книга Узбекистана)
      - Государственные программы по охране природы
      - Ссылки: UNEP, UN Uzbekistan, IISD, WorldBank
  
  1.2 Геймификация в образовании (3-4 стр)
      - Определение геймификации (Deterding et al., 2011)
      - Психологические основы: мотивация, вовлечённость, reward systems
      - Теория самодетерминации и внешняя/внутренняя мотивация
      - Эффективность геймификации в экологическом образовании (coralQuest, EcoHeroes)
      - Форматы: викторины, симуляторы, ролевые игры
      - Исследования Kahoot, Quizizz — влияние на усвоение материала
      - Таксономия Блума: от запоминания до применения через игровые механики
  
  1.3 Анализ существующих аналогов (4-5 стр)
      - Таблица сравнения 5-6 аналогов:
        | Система | Тип | Язык | Экологический контент | Геймификация | Платформа |
      - Kahoot (общий quiz, не экологический)
      - Quizizz (аналогичный)
      - EcoHeroes (экологический, мобильный, MIT App Inventor)
      - coralQuest (морская экология, лидерборд)
      - EPA Games (экологический, но не викторина)
      - Viktorina UZ (узбекский quiz, но не экологический)
      - Вывод: ниша узбекскоязычных экологических викторин пустая
  
  1.4 Требования к разрабатываемой системе (2-3 стр)
      - Функциональные требования (12-15 пунктов)
      - Нефункциональные требования (производительность, безопасность, доступность)
      - Требования к контенту (язык, тематика, источники)
  
  1.5 Обоснование выбора технологий (2-3 стр)
      - Django REST Framework vs Flask/FastAPI/Node.js
      - React vs Vue/Angular
      - PostgreSQL vs MySQL/MongoDB
      - Docker + Coolify для деплоя
      - Сравнительная таблица технологий
  
  Выводы по главе 1 (0.5 стр)
  ```

**Проверка:** Файл существует, объём 8000+ слов, ≥5 источников цитируется
**Коммит:** `docs: ВКР — Глава 1 (анализ предметной области, аналоги, требования)`

---

### [ ] 11.3 Написать Главу 2 — Проектная часть

**Что сделать:**
- Полностью переписать `docs/vkr/chapter2_design.md`
- Объём: 15-20 страниц (≈ 8000-10000 слов)
- Структура:
  ```
  ГЛАВА 2. ПРОЕКТИРОВАНИЕ СИСТЕМЫ
  
  2.1 Архитектура системы (2-3 стр)
      - Клиент-серверная архитектура
      - Компонентная диаграмма (текстовое описание + Mermaid)
      - Взаимодействие: React (Vite) → nginx → Django REST → PostgreSQL
      - JWT аутентификация: access/refresh token flow
      - Docker Compose сервисы и их взаимодействие
      - Рисунок X.1 — Архитектура системы
  
  2.2 Проектирование базы данных (4-5 стр)
      - ER-диаграмма всех сущностей (текстовое Mermaid описание)
      - Описание каждой таблицы/модели:
        Player, Question, Answer, QuizSession, QuizAnswer, DailyChallenge,
        Achievement, PlayerAchievement, MiniGameScore, LeaderboardEntry,
        EducationalContent, EcoFact
      - Обоснование выбора типов данных
      - Индексы и ограничения (unique_together, validators)
      - Рисунок X.2 — ER-диаграмма базы данных
  
  2.3 Проектирование REST API (3-4 стр)
      - Принципы REST API в проекте
      - Таблица всех endpoints (метод, путь, авторизация, описание)
      - Примеры запросов/ответов для ключевых endpoints
      - JWT аутентификация: заголовок Authorization: Bearer <token>
      - Пагинация ответов
      - Обработка ошибок (400, 401, 403, 404)
  
  2.4 Алгоритм системы оценивания (2-3 стр)
      - Формула расчёта очков (streak_multiplier × time_factor × BASE)
      - Таблица streak multiplier
      - Пример расчёта для разных сценариев
      - Алгоритм проверки достижений
      - Псевдокод check_achievements
      - Рисунок X.3 — Блок-схема расчёта очков
  
  2.5 Проектирование интерфейса (3-4 стр)
      - Use Case диаграмма (текстовое описание)
      - Wireframes страниц (текстовое описание макетов):
        Главное меню → Квиз-экран → Результаты → Мини-игра → Профиль
      - Принципы UX: доступность, отклик <100мс, мобильный дизайн
      - Цветовая схема (зелёная тематика, экологические цвета)
      - Рисунок X.4 — Прототип главного меню
      - Рисунок X.5 — Прототип экрана вопроса
  
  Выводы по главе 2 (0.5 стр)
  ```

**Проверка:** Файл существует, объём 8000+ слов
**Коммит:** `docs: ВКР — Глава 2 (архитектура, БД, API, алгоритм оценивания)`

---

### [ ] 11.4 Написать Главу 3 — Реализация

**Что сделать:**
- Полностью переписать `docs/vkr/chapter3_implementation.md`
- Объём: 15-20 страниц (≈ 8000-10000 слов)
- Структура:
  ```
  ГЛАВА 3. РЕАЛИЗАЦИЯ СИСТЕМЫ
  
  3.1 Реализация серверной части (4-5 стр)
      - Django проект: структура, settings (dev/prod), BASE_DIR
      - Модель Question: код + объяснение полей
      - QuizService.calculate_score: листинг + объяснение алгоритма
      - QuizService.submit_answer: листинг ключевых частей
      - QuizService.end_session + обновление лидерборда через signal
      - API View QuizSessionStartView: код + объяснение
      - Рисунок X.1 — Скриншот Django Admin (Question)
  
  3.2 Реализация клиентской части (4-5 стр)
      - Zustand quizStore: структура состояния
      - QuizPlayPage: компонентная иерархия, useEffect для old quiz
      - Timer: SVG circle + useEffect interval
      - AnswerButton: state machine (idle/selected/correct/incorrect)
      - ExplanationPanel: показ после ответа
      - Рисунок X.2 — Скриншот экрана вопроса в браузере
      - Рисунок X.3 — Скриншот результатов квиза
  
  3.3 Реализация мини-игры (3-4 стр)
      - HTML5 Drag and Drop API: draggable, onDragStart, onDrop
      - Touch Events: touchstart/touchend для мобильных
      - SortingGame компонент: state machine игры
      - Алгоритм проверки правильности бина
      - Рисунок X.4 — Скриншот мини-игры сортировки
  
  3.4 Аутентификация и безопасность (2-3 стр)
      - JWT: access (15 мин) + refresh (7 дней) токены
      - Анонимный пользователь: session_key, auto-create, claim account
      - CORS настройки для prod
      - HTTPS через Traefik + Let's Encrypt
      - Валидация на уровне сериализаторов DRF
  
  3.5 Деплой и DevOps (2-3 стр)
      - Docker Compose: 4 сервиса (postgres, backend, frontend, nginx)
      - Dockerfile backend: python 3.12-slim, uv, gunicorn
      - Dockerfile frontend: Node 20 multi-stage, nginx:alpine
      - Coolify: GUI деплой, auto SSL, rollback
      - GitHub → Coolify CI/CD (manual deploy)
      - Рисунок X.5 — Скриншот Coolify dashboard
  
  Выводы по главе 3 (0.5 стр)
  ```
- Включить реальные фрагменты кода (листинги) из проекта

**Проверка:** Файл существует, объём 8000+ слов, включает листинги кода
**Коммит:** `docs: ВКР — Глава 3 (реализация сервера, клиента, мини-игры, деплой)`

---

### [ ] 11.5 Написать Главу 4 — Тестирование

**Что сделать:**
- Полностью переписать `docs/vkr/chapter4_testing.md`
- Объём: 5-8 страниц (≈ 2500-4000 слов)
- Структура:
  ```
  ГЛАВА 4. ТЕСТИРОВАНИЕ И ОЦЕНКА

  4.1 Стратегия тестирования (1 стр)
      - Пирамида тестирования: Unit → Integration → E2E
      - Инструменты: pytest (backend), TypeScript strict mode (frontend)

  4.2 Модульное тестирование (2-3 стр)
      - Backend: pytest + pytest-django
      - Таблица тест-кейсов по модулям:
        | Класс теста | Кол-во тестов | Покрытие |
        | TestQuizService | 10 | scoring, streak, achievements |
        | TestQuestionModel | 5 | validation, ordering |
        | TestQuizAPIFlow | 8 | start/answer/end |
      - Результат: N тестов пройдено, 0 failed
      - Листинг ключевого теста (TestCalculateScore)
      - Рисунок X.1 — Вывод pytest -v

  4.3 Интеграционное тестирование (1-2 стр)
      - Full quiz flow test: start → answer×10 → end → check leaderboard
      - Тест сигнала лидерборда
      - Тест анонимной аутентификации и claim

  4.4 Тестирование интерфейса (1-2 стр)
      - Тестирование в Chrome DevTools (mobile emulation)
      - Проверка на реальном мобильном устройстве (touch events)
      - Браузерная совместимость: Chrome, Firefox, Safari
      - Рисунок X.2 — Скриншот на мобильном устройстве

  4.5 Нагрузочное тестирование (0.5-1 стр)
      - Среда: production сервер (89.167.60.96)
      - Инструмент: Apache Benchmark / curl
      - Результат: X req/sec при N одновременных пользователях

  Выводы по главе 4 (0.5 стр)
  ```

**Проверка:** Файл существует, объём 2500+ слов
**Коммит:** `docs: ВКР — Глава 4 (тестирование: unit, integration, UI)`

---

### [ ] 11.6 Написать Заключение, Список литературы, Приложения

**Что сделать:**
- Переписать `docs/vkr/conclusion.md` (2-3 стр):
  - Что было сделано (перечисление выполненных задач)
  - Научная новизна (первая экологическая викторина на узбекском)
  - Практическая значимость
  - Перспективы развития (мобильное приложение, AR, мультиплеер)

- Полностью переписать `docs/vkr/bibliography.md` — 20+ источников в ГОСТ Р 7.0.5-2008:
  - Отечественные источники: постановления правительства Узбекистана по экологии
  - Международные: UNEP, FAO, UNESCO доклады по экологии
  - Научные статьи: геймификация в образовании (Deterding 2011, Hamari 2014, Deci 2000)
  - Книги: Django docs, React docs
  - Интернет-ресурсы (не более 5)

- Переписать `docs/vkr/appendix_a_code.md`:
  - QuizService.calculate_score (полный листинг)
  - QuizService.submit_answer (полный листинг)
  - QuestionSerializer (полный листинг)
  - quizStore.ts (полный листинг)
  - Timer.tsx (полный листинг)

- Переписать `docs/vkr/appendix_b_screenshots.md`:
  - Список и описания 8-10 скриншотов приложения
  - (Скриншоты будут добавлены после деплоя)

- Переписать `docs/vkr/appendix_c_er_diagram.md`:
  - Полная ER-диаграмма в Mermaid синтаксисе
  - Описание каждой связи

- Создать `docs/vkr/appendix_d_api_docs.md`:
  - Полная документация всех API endpoints
  - Для каждого: Method, URL, Auth, Request body, Response, Errors

**Проверка:** Все файлы в docs/vkr/ существуют, bibliography.md содержит 20+ источников
**Коммит:** `docs: ВКР — Заключение, Библиография, Приложения А-Г`

---

## Phase 12: Deploy + Презентация

### [ ] 12.1 Задеплоить на production и протестировать

**Что сделать:**
- Проверить `docker-compose.yml` — убедиться что конфигурация актуальна
- Подключиться по SSH: `ssh -p 2222 deploy@89.167.60.96`
- Выполнить на сервере:
  ```bash
  cd /opt/coolify/applications/<app-id>
  git pull origin main
  docker compose up --build -d
  docker compose exec backend uv run python manage.py migrate
  docker compose exec backend uv run python manage.py loaddata fixtures/questions.json fixtures/quiz_achievements.json fixtures/educational_content.json fixtures/eco_facts.json
  ```
- Проверить: `curl https://ecogame.fullfocus.dev/api/v1/game/quiz/questions/`
- Проверить: `curl https://ecogame.fullfocus.dev/api/v1/game/quiz/daily/` — с JWT токеном
- Открыть https://ecogame.fullfocus.dev в браузере:
  - Анонимный вход → квиз Quick play → 10 вопросов → результаты → лидерборд
  - Мини-игра → сортировка → результат
  - Регистрация → профиль → достижения

**Проверка:** Все страницы работают, квиз завершается, счёт попадает в лидерборд
**Коммит:** `chore: production deploy quiz pivot — ecogame.fullfocus.dev`

---

### [ ] 12.2 Создать презентацию (Gamma)

**Что сделать:**
- Создать презентацию через Gamma (https://gamma.app) или в Google Slides
- 12-15 слайдов:
  1. Титульный: EcoGame — Экологическая викторина (имя, группа, научрук)
  2. Актуальность: экологические проблемы Узбекистана
  3. Нехватка решений: нет экологических викторин на узбекском
  4. Цель и задачи
  5. Демо: скриншоты главного меню + режимы квиза
  6. Демо: экран вопроса с таймером и стриком
  7. Демо: результаты + достижения
  8. Мини-игра: сортировка отходов
  9. Архитектура системы
  10. База данных: ER-диаграмма
  11. Тестирование: N тестов, результаты
  12. Deploy: ecogame.fullfocus.dev — демо в прямом эфире
  13. Заключение: что сделано + научная новизна + перспективы
  14. Список литературы (ключевые источники)
  15. Спасибо + QR-код на сайт

- Сохранить ссылку на презентацию в `docs/presentation/README.md`

**Проверка:** Презентация существует, ссылка сохранена, 12-15 слайдов
**Коммит:** `docs: создать ссылку на презентацию к защите`
