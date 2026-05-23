from django.db.models import Count, Q, Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.game.models import GameProgress, PlayerAchievement

from .models import LeaderboardEntry


@receiver(post_save, sender=GameProgress)
def update_leaderboard_on_progress(sender: type, instance: GameProgress, **kwargs: object) -> None:
    """Обновить лидерборд при изменении прогресса игрока."""
    player = instance.player
    stats = GameProgress.objects.filter(player=player).aggregate(
        total=Sum("score"),
        completed=Count("id", filter=Q(completed=True)),
    )
    achievement_count = PlayerAchievement.objects.filter(player=player).count()

    entry, _ = LeaderboardEntry.objects.get_or_create(player=player)
    entry.total_score = stats["total"] or 0
    entry.levels_completed = stats["completed"] or 0
    entry.achievements_count = achievement_count
    entry.save(
        update_fields=["total_score", "levels_completed", "achievements_count", "updated_at"]
    )

    # Пересчитать ранги всех игроков
    for rank, e in enumerate(LeaderboardEntry.objects.order_by("-total_score"), start=1):
        if e.rank != rank:
            LeaderboardEntry.objects.filter(pk=e.pk).update(rank=rank)


@receiver(post_save, sender=PlayerAchievement)
def update_leaderboard_on_achievement(
    sender: type, instance: PlayerAchievement, **kwargs: object
) -> None:
    """Обновить счётчик достижений при разблокировке."""
    player = instance.player
    count = PlayerAchievement.objects.filter(player=player).count()
    LeaderboardEntry.objects.filter(player=player).update(achievements_count=count)
