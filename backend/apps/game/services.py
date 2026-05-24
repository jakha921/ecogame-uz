from __future__ import annotations

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.accounts.models import Player

from .models import (
    Achievement,
    ConditionType,
    GameProgress,
    GameSession,
    Level,
    PlayerAchievement,
)

LEVEL_COMPLETION_THRESHOLD = 80.0


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
