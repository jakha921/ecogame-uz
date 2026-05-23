from django.conf import settings
from django.db import models


class LeaderboardEntry(models.Model):
    """Денормализованная таблица лидеров для быстрого чтения."""

    player = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="leaderboard_entry",
        verbose_name="Игрок",
    )
    total_score = models.PositiveIntegerField(default=0, verbose_name="Общий счёт", db_index=True)
    levels_completed = models.PositiveSmallIntegerField(default=0, verbose_name="Пройдено уровней")
    achievements_count = models.PositiveSmallIntegerField(default=0, verbose_name="Достижений")
    rank = models.PositiveIntegerField(default=0, db_index=True, verbose_name="Ранг")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Запись лидерборда"
        verbose_name_plural = "Лидерборд"
        ordering = ["rank"]

    def __str__(self) -> str:
        return f"#{self.rank} {self.player} — {self.total_score}pts"
