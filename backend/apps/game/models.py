from django.conf import settings
from django.db import models


class ActionCategory(models.TextChoices):
    FLORA = "FLORA", "Флора"
    WATER = "WATER", "Вода"
    WASTE = "WASTE", "Отходы"
    ENERGY = "ENERGY", "Энергия"
    FAUNA = "FAUNA", "Фауна"


class Level(models.Model):
    """Определение игрового уровня."""

    number = models.PositiveSmallIntegerField(unique=True, verbose_name="Номер уровня")
    name_uz = models.CharField(max_length=100, verbose_name="Название (уз)")
    description_uz = models.TextField(verbose_name="Описание (уз)")
    required_score = models.PositiveIntegerField(default=0, verbose_name="Очков для разблокировки")
    map_config = models.JSONField(default=dict, verbose_name="Конфигурация карты")
    ecosystem_initial = models.JSONField(
        default=dict,
        verbose_name="Начальные значения экосистемы",
        help_text='Пример: {"air": 30, "water": 25, "soil": 20, "biodiversity": 15}',
    )

    class Meta:
        verbose_name = "Уровень"
        verbose_name_plural = "Уровни"
        ordering = ["number"]

    def __str__(self) -> str:
        return f"Уровень {self.number}: {self.name_uz}"


class EcoAction(models.Model):
    """Каталог экологических действий игрока."""

    key = models.CharField(max_length=50, unique=True, verbose_name="Ключ")
    name_uz = models.CharField(max_length=100, verbose_name="Название (уз)")
    description_uz = models.TextField(verbose_name="Описание (уз)")
    category = models.CharField(
        max_length=10, choices=ActionCategory.choices, verbose_name="Категория"
    )
    score_value = models.PositiveIntegerField(default=10, verbose_name="Очки за действие")
    cost = models.PositiveIntegerField(default=10, verbose_name="Стоимость (эко-монеты)")
    air_impact = models.FloatField(default=0.0, verbose_name="Влияние на воздух")
    water_impact = models.FloatField(default=0.0, verbose_name="Влияние на воду")
    soil_impact = models.FloatField(default=0.0, verbose_name="Влияние на почву")
    biodiversity_impact = models.FloatField(default=0.0, verbose_name="Влияние на биоразнообразие")
    cooldown_seconds = models.PositiveIntegerField(default=5, verbose_name="Кулдаун (сек)")
    unlock_level = models.ForeignKey(
        Level,
        on_delete=models.CASCADE,
        related_name="actions",
        verbose_name="Минимальный уровень",
    )
    sprite_key = models.CharField(max_length=50, default="default", verbose_name="Ключ спрайта")

    class Meta:
        verbose_name = "Экодействие"
        verbose_name_plural = "Экодействия"
        ordering = ["category", "key"]

    def __str__(self) -> str:
        return f"{self.name_uz} ({self.category})"


class GameSession(models.Model):
    """Игровая сессия игрока."""

    player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name="Игрок",
    )
    level = models.ForeignKey(Level, on_delete=models.CASCADE, verbose_name="Уровень")
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Начало")
    ended_at = models.DateTimeField(null=True, blank=True, verbose_name="Конец")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Сессия"
        verbose_name_plural = "Сессии"
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"{self.player} — Level {self.level.number} ({self.started_at:%Y-%m-%d})"


class GameProgress(models.Model):
    """Прогресс игрока по уровню."""

    player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="progress",
        verbose_name="Игрок",
    )
    level = models.ForeignKey(Level, on_delete=models.CASCADE, verbose_name="Уровень")
    score = models.PositiveIntegerField(default=0, verbose_name="Очки")
    air_quality = models.FloatField(default=0.0, verbose_name="Качество воздуха")
    water_purity = models.FloatField(default=0.0, verbose_name="Чистота воды")
    soil_health = models.FloatField(default=0.0, verbose_name="Здоровье почвы")
    biodiversity = models.FloatField(default=0.0, verbose_name="Биоразнообразие")
    actions_performed = models.JSONField(
        default=dict,
        verbose_name="Выполненные действия",
        help_text='Пример: {"plant_tree": 5, "clean_water": 3}',
    )
    world_state = models.JSONField(
        default=dict,
        verbose_name="Состояние мира",
        help_text='{"placed_objects": [...], "resources": 75}',
    )
    completed = models.BooleanField(default=False, verbose_name="Завершён")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата завершения")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлён")

    class Meta:
        verbose_name = "Прогресс"
        verbose_name_plural = "Прогресс игроков"
        unique_together = ("player", "level")
        ordering = ["level__number"]

    def __str__(self) -> str:
        status = "✓" if self.completed else "..."
        return f"{self.player} — Level {self.level.number} [{status}] {self.score}pts"


class ActionLog(models.Model):
    """Лог выполненных действий."""

    session = models.ForeignKey(
        GameSession,
        on_delete=models.CASCADE,
        related_name="action_logs",
        verbose_name="Сессия",
    )
    action = models.ForeignKey(EcoAction, on_delete=models.CASCADE, verbose_name="Действие")
    performed_at = models.DateTimeField(auto_now_add=True, verbose_name="Время")
    position_x = models.FloatField(default=0.0, verbose_name="Позиция X")
    position_y = models.FloatField(default=0.0, verbose_name="Позиция Y")
    result_delta = models.JSONField(
        default=dict,
        verbose_name="Изменения индикаторов",
    )

    class Meta:
        verbose_name = "Лог действия"
        verbose_name_plural = "Лог действий"
        ordering = ["-performed_at"]

    def __str__(self) -> str:
        return f"{self.action.key} @ {self.performed_at:%H:%M:%S}"


class ConditionType(models.TextChoices):
    SCORE = "SCORE", "Очки"
    ACTION_COUNT = "ACTION_COUNT", "Количество действий"
    LEVEL_COMPLETE = "LEVEL_COMPLETE", "Завершение уровня"
    INDICATOR = "INDICATOR", "Значение индикатора"


class Achievement(models.Model):
    """Определение достижения."""

    key = models.CharField(max_length=50, unique=True, verbose_name="Ключ")
    name_uz = models.CharField(max_length=100, verbose_name="Название (уз)")
    description_uz = models.TextField(verbose_name="Описание (уз)")
    icon = models.CharField(max_length=50, default="star", verbose_name="Иконка")
    condition_type = models.CharField(
        max_length=20, choices=ConditionType.choices, verbose_name="Тип условия"
    )
    condition_value = models.JSONField(
        default=dict,
        verbose_name="Значение условия",
        help_text="ACTION_COUNT: {'action_key': 'plant_tree', 'count': 10}",
    )

    class Meta:
        verbose_name = "Достижение"
        verbose_name_plural = "Достижения"
        ordering = ["condition_type", "key"]

    def __str__(self) -> str:
        return f"{self.name_uz} ({self.condition_type})"


class PlayerAchievement(models.Model):
    """Связь игрок — достижение."""

    player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="achievements",
        verbose_name="Игрок",
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name="players",
        verbose_name="Достижение",
    )
    unlocked_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата разблокировки")

    class Meta:
        verbose_name = "Достижение игрока"
        verbose_name_plural = "Достижения игроков"
        unique_together = ("player", "achievement")

    def __str__(self) -> str:
        return f"{self.player} — {self.achievement.name_uz}"
