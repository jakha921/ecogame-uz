from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Player

from .models import (
    Achievement,
    ActionLog,
    ConditionType,
    EcoAction,
    GameProgress,
    GameSession,
    Level,
    PlayerAchievement,
)

LEVEL_COMPLETION_THRESHOLD = 80.0
INDICATOR_MAX = 100.0
INDICATOR_MIN = 0.0
ACTION_IMPACT_MULTIPLIER = 10.0

# Slow passive degradation per second (applied per tick)
DEGRADATION = {
    "air": 0.0002,
    "water": 0.0015,
    "soil": 0.001,
    "biodiversity": 0.0025,
}


class GameService:
    """Central business logic for the game. All mutations go through here."""

    @staticmethod
    def start_session(player: Player, level: Level) -> GameSession:
        """Start a game session, creating GameProgress if it doesn't exist yet."""
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
        """End an active session and update the player's total_score."""
        with transaction.atomic():
            session.ended_at = timezone.now()
            session.is_active = False
            session.save(update_fields=["ended_at", "is_active"])

            progress = GameProgress.objects.select_related("player", "level").get(
                player=session.player,
                level=session.level,
            )

            # Sync player total_score from all progress
            from django.db.models import Sum

            total = (
                GameProgress.objects.filter(player=session.player).aggregate(total=Sum("score"))[
                    "total"
                ]
                or 0
            )
            Player.objects.filter(pk=session.player.pk).update(total_score=total)

            return progress

    @staticmethod
    def perform_actions(session: GameSession, actions: list[dict]) -> GameProgress:
        """Process a batch of player actions and update ecosystem indicators.

        Each action dict: {"action_key": str, "position_x": float, "position_y": float}
        """
        with transaction.atomic():
            progress = GameProgress.objects.select_related("level", "player").get(
                player=session.player,
                level=session.level,
            )

            action_keys = [a["action_key"] for a in actions]
            eco_actions = {ea.key: ea for ea in EcoAction.objects.filter(key__in=action_keys)}

            for action_data in actions:
                action = eco_actions.get(action_data["action_key"])
                if action is None:
                    continue

                delta = GameService.calculate_ecosystem(progress, action)

                progress.air_quality = delta["air"]
                progress.water_purity = delta["water"]
                progress.soil_health = delta["soil"]
                progress.biodiversity = delta["biodiversity"]
                progress.score += action.score_value

                # Track action counts
                counts = progress.actions_performed
                counts[action.key] = counts.get(action.key, 0) + 1
                progress.actions_performed = counts

                ActionLog.objects.create(
                    session=session,
                    action=action,
                    position_x=action_data.get("position_x", 0.0),
                    position_y=action_data.get("position_y", 0.0),
                    result_delta=delta,
                )

            if GameService.check_level_completion(progress):
                progress.completed = True
                progress.completed_at = timezone.now()

            progress.save()

            GameService.check_achievements(session.player, progress)

            return progress

    @staticmethod
    def calculate_ecosystem(progress: GameProgress, action: EcoAction) -> dict:
        """Calculate new ecosystem indicator values after an action.

        Returns clamped dict: {air, water, soil, biodiversity}
        """

        def clamp(value: float) -> float:
            return max(INDICATOR_MIN, min(INDICATOR_MAX, value))

        air = clamp(progress.air_quality + action.air_impact * ACTION_IMPACT_MULTIPLIER)
        water = clamp(progress.water_purity + action.water_impact * ACTION_IMPACT_MULTIPLIER)
        soil = clamp(progress.soil_health + action.soil_impact * ACTION_IMPACT_MULTIPLIER)
        biodiversity = clamp(
            progress.biodiversity + action.biodiversity_impact * ACTION_IMPACT_MULTIPLIER
        )

        # Compound: high biodiversity boosts all indicators slightly
        if biodiversity > 50:
            bonus = (biodiversity - 50) / 10 * 0.005
            air = clamp(air + bonus)
            water = clamp(water + bonus)
            soil = clamp(soil + bonus)

        return {"air": air, "water": water, "soil": soil, "biodiversity": biodiversity}

    @staticmethod
    def check_achievements(player: Player, progress: GameProgress) -> list[Achievement]:
        """Check and unlock achievements. Returns newly unlocked achievements."""
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

        if ach.condition_type == ConditionType.ACTION_COUNT:
            action_key = cond.get("action_key", "")
            required = cond.get("count", 1)
            performed = progress.actions_performed.get(action_key, 0)
            return performed >= required

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
        """Level is complete when all 4 indicators reach 80%."""
        return (
            progress.air_quality >= LEVEL_COMPLETION_THRESHOLD
            and progress.water_purity >= LEVEL_COMPLETION_THRESHOLD
            and progress.soil_health >= LEVEL_COMPLETION_THRESHOLD
            and progress.biodiversity >= LEVEL_COMPLETION_THRESHOLD
        )
