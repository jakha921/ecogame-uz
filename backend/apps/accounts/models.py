from django.contrib.auth.models import AbstractUser
from django.db import models


class Player(AbstractUser):
    """Расширенная модель игрока с игровыми данными."""

    nickname = models.CharField(max_length=50, unique=True, verbose_name="Ник")
    avatar = models.CharField(max_length=50, default="default", verbose_name="Аватар")
    total_score = models.PositiveIntegerField(default=0, verbose_name="Общий счёт")

    class Meta:
        verbose_name = "Игрок"
        verbose_name_plural = "Игроки"
        ordering = ["-total_score"]

    def __str__(self) -> str:
        return self.nickname or self.username
