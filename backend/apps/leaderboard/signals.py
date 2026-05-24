from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import Player
from apps.game.models import PlayerAchievement, QuizSession

from .models import LeaderboardEntry


@receiver(post_save, sender=QuizSession)
def update_leaderboard_on_quiz(sender: type, instance: QuizSession, **kwargs: object) -> None:
    """Update leaderboard when a quiz session is finished."""
    if instance.finished_at is None:
        return

    player = instance.player
    quiz_total = (
        QuizSession.objects.filter(player=player, finished_at__isnull=False).aggregate(
            total=Sum("score")
        )["total"]
        or 0
    )

    Player.objects.filter(pk=player.pk).update(total_score=quiz_total)

    quizzes_count = QuizSession.objects.filter(player=player, finished_at__isnull=False).count()
    achievement_count = PlayerAchievement.objects.filter(player=player).count()

    entry, _ = LeaderboardEntry.objects.get_or_create(player=player)
    entry.total_score = quiz_total
    entry.levels_completed = quizzes_count  # repurposed: counts completed quizzes
    entry.achievements_count = achievement_count
    entry.save(
        update_fields=["total_score", "levels_completed", "achievements_count", "updated_at"]
    )

    for rank, e in enumerate(LeaderboardEntry.objects.order_by("-total_score"), start=1):
        if e.rank != rank:
            LeaderboardEntry.objects.filter(pk=e.pk).update(rank=rank)


@receiver(post_save, sender=PlayerAchievement)
def update_leaderboard_on_achievement(
    sender: type, instance: PlayerAchievement, **kwargs: object
) -> None:
    """Update achievement count on leaderboard when an achievement is unlocked."""
    count = PlayerAchievement.objects.filter(player=instance.player).count()
    LeaderboardEntry.objects.filter(player=instance.player).update(achievements_count=count)
