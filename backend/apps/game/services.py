from __future__ import annotations

import math
import random
from datetime import date

from django.db import transaction
from django.db.models import Max as models_max
from django.db.models import Sum
from django.utils import timezone

from apps.accounts.models import Player

from .models import (
    Achievement,
    ActionCategory,
    Answer,
    ConditionType,
    DailyChallenge,
    GameProgress,
    GameSession,
    Level,
    PlayerAchievement,
    Question,
    QuizAnswer,
    QuizMode,
    QuizSession,
)

LEVEL_COMPLETION_THRESHOLD = 80.0


# ─── Legacy game service ─────────────────────────────────────────────────────


class GameService:
    """Legacy game session service (kept for backward compatibility)."""

    @staticmethod
    def start_session(player: Player, level: Level) -> GameSession:
        with transaction.atomic():
            session = GameSession.objects.create(player=player, level=level)
            GameProgress.objects.get_or_create(
                player=player,
                level=level,
                defaults={
                    "air_quality": float(level.ecosystem_initial.get("air", 30)),
                    "water_purity": float(level.ecosystem_initial.get("water", 25)),
                    "soil_health": float(level.ecosystem_initial.get("soil", 20)),
                    "biodiversity": float(level.ecosystem_initial.get("biodiversity", 15)),
                },
            )
            return session

    @staticmethod
    def end_session(session: GameSession) -> GameProgress:
        with transaction.atomic():
            session.ended_at = timezone.now()
            session.is_active = False
            session.save(update_fields=["ended_at", "is_active"])

            progress = GameProgress.objects.select_related("player", "level").get(
                player=session.player,
                level=session.level,
            )

            total = (
                GameProgress.objects.filter(player=session.player).aggregate(total=Sum("score"))[
                    "total"
                ]
                or 0
            )
            Player.objects.filter(pk=session.player.pk).update(total_score=total)

            return progress

    @staticmethod
    def check_achievements(player: Player, progress: GameProgress) -> list[Achievement]:
        already_unlocked = set(
            PlayerAchievement.objects.filter(player=player).values_list("achievement_id", flat=True)
        )
        all_achievements = Achievement.objects.exclude(pk__in=already_unlocked)

        newly_unlocked: list[Achievement] = []
        for ach in all_achievements:
            if GameService._is_achievement_unlocked(ach, player, progress):
                PlayerAchievement.objects.get_or_create(player=player, achievement=ach)
                newly_unlocked.append(ach)

        return newly_unlocked

    @staticmethod
    def _is_achievement_unlocked(ach: Achievement, player: Player, progress: GameProgress) -> bool:
        cond = ach.condition_value

        if ach.condition_type == ConditionType.SCORE:
            return progress.score >= cond.get("min_score", 0)

        if ach.condition_type == ConditionType.LEVEL_COMPLETE:
            level_number = cond.get("level_number", 1)
            return progress.completed and progress.level.number == level_number

        if ach.condition_type == ConditionType.INDICATOR:
            indicator = cond.get("indicator", "air")
            min_value = cond.get("min_value", 80)
            current = {
                "air": progress.air_quality,
                "water": progress.water_purity,
                "soil": progress.soil_health,
                "biodiversity": progress.biodiversity,
            }.get(indicator, 0)
            return current >= min_value

        return False

    @staticmethod
    def check_level_completion(progress: GameProgress) -> bool:
        return (
            progress.air_quality >= LEVEL_COMPLETION_THRESHOLD
            and progress.water_purity >= LEVEL_COMPLETION_THRESHOLD
            and progress.soil_health >= LEVEL_COMPLETION_THRESHOLD
            and progress.biodiversity >= LEVEL_COMPLETION_THRESHOLD
        )


# ─── Quiz service ─────────────────────────────────────────────────────────────


class QuizService:
    """Business logic for the quiz game."""

    BASE_POINTS = 100
    # Streak index: how many correct in a row BEFORE this answer
    STREAK_MULTIPLIERS: dict[int, float] = {0: 1.0, 1: 1.0, 2: 1.5, 3: 2.0}
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
        multiplier = QuizService.STREAK_MULTIPLIERS.get(streak, QuizService.STREAK_MAX_MULTIPLIER)
        time_limit_ms = time_limit * 1000
        time_ratio = max(0.0, 1.0 - time_spent_ms / time_limit_ms)
        time_factor = 1.0 + 0.5 * time_ratio
        return math.floor(QuizService.BASE_POINTS * multiplier * time_factor)

    @staticmethod
    def get_questions_for_mode(mode: str, category: str | None, count: int = 10) -> list[Question]:
        qs = Question.objects.filter(is_active=True).prefetch_related("answers")
        if mode == QuizMode.CATEGORY and category:
            qs = qs.filter(category=category)
        questions = list(qs)
        random.shuffle(questions)
        if mode in (QuizMode.QUICK, QuizMode.DAILY):
            questions = questions[:count]
        elif mode == QuizMode.MARATHON:
            questions = questions[: QuizService.MARATHON_MAX_QUESTIONS]
        return questions

    @staticmethod
    def start_session(
        player: Player, mode: str, category: str | None = None
    ) -> tuple[QuizSession, list[Question]]:
        """Create a QuizSession and return it together with the question list."""
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

        # Streak before this answer (used for score calculation)
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

    @staticmethod
    def end_session(session: QuizSession) -> dict:
        session.finished_at = timezone.now()
        session.save(update_fields=["finished_at"])

        accuracy = (
            session.correct_count / session.total_questions if session.total_questions > 0 else 0.0
        )

        player = session.player
        total = (
            QuizSession.objects.filter(player=player, finished_at__isnull=False).aggregate(
                t=Sum("score")
            )["t"]
            or 0
        )
        player.__class__.objects.filter(pk=player.pk).update(total_score=total)

        achievements = QuizService.check_quiz_achievements(player, session)

        return {
            "session": session,
            "accuracy": round(accuracy, 3),
            "rank_title": QuizService.get_rank_title(total),
            "achievements_unlocked": achievements,
        }

    @staticmethod
    def get_daily_challenge(target_date: date | None = None) -> DailyChallenge:
        if target_date is None:
            target_date = date.today()
        challenge, created = DailyChallenge.objects.get_or_create(
            date=target_date,
            defaults={"bonus_score": 50},
        )
        if created:
            questions = list(Question.objects.filter(is_active=True).order_by("?")[:10])
            challenge.questions.set(questions)
        return challenge

    @staticmethod
    def get_player_stats(player: Player) -> dict:
        sessions = QuizSession.objects.filter(player=player, finished_at__isnull=False)
        total_quizzes = sessions.count()
        total_correct = sessions.aggregate(t=Sum("correct_count"))["t"] or 0
        total_questions = sessions.aggregate(t=Sum("total_questions"))["t"] or 0
        best_streak = sessions.aggregate(m=models_max("max_streak"))["m"] or 0
        accuracy = total_correct / total_questions if total_questions > 0 else 0.0

        per_category: dict[str, dict] = {}
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
            "daily_streak": 0,
            "rank_title": QuizService.get_rank_title(player.total_score),
            "per_category": per_category,
        }

    @staticmethod
    def check_quiz_achievements(player: Player, session: QuizSession) -> list[Achievement]:
        all_achievements = Achievement.objects.all()
        earned = set(
            PlayerAchievement.objects.filter(player=player).values_list("achievement_id", flat=True)
        )
        new_achievements: list[Achievement] = []

        total_quizzes = QuizSession.objects.filter(player=player, finished_at__isnull=False).count()

        for ach in all_achievements:
            if ach.id in earned:
                continue
            cv = ach.condition_value
            unlocked = False

            if ach.condition_type == ConditionType.SCORE:
                unlocked = player.total_score >= cv.get("min_score", 0)
            elif ach.condition_type == ConditionType.QUIZ_COUNT:
                unlocked = total_quizzes >= cv.get("count", 1)
            elif ach.condition_type == ConditionType.STREAK:
                unlocked = session.max_streak >= cv.get("min_streak", 5)

            if unlocked:
                PlayerAchievement.objects.create(player=player, achievement=ach)
                new_achievements.append(ach)
                earned.add(ach.id)

        return new_achievements
