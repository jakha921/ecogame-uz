from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class ActionCategory(models.TextChoices):
    FLORA = "FLORA", "Флора"
    WATER = "WATER", "Вода"
    WASTE = "WASTE", "Отходы"
    ENERGY = "ENERGY", "Энергия"
    FAUNA = "FAUNA", "Фауна"


class QuestionType(models.TextChoices):
    MCQ = "MCQ", "Ko'p tanlovli"
    TRUE_FALSE = "TRUE_FALSE", "To'g'ri/Noto'g'ri"
    SCENARIO = "SCENARIO", "Senariy"


class QuizMode(models.TextChoices):
    QUICK = "QUICK", "Tezkor o'yin"
    CATEGORY = "CATEGORY", "Kategoriya bo'yicha"
    DAILY = "DAILY", "Kunlik vazifa"
    MARATHON = "MARATHON", "Marafon"


class ConditionType(models.TextChoices):
    SCORE = "SCORE", "Очки"
    ACTION_COUNT = "ACTION_COUNT", "Количество действий"
    LEVEL_COMPLETE = "LEVEL_COMPLETE", "Завершение уровня"
    INDICATOR = "INDICATOR", "Значение индикатора"
    QUIZ_COUNT = "QUIZ_COUNT", "Количество викторин"
    STREAK = "STREAK", "Серия ответов"
    DAILY_STREAK = "DAILY_STREAK", "Ежедневная серия"
    CATEGORY_MASTER = "CATEGORY_MASTER", "Мастер категории"


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
    )

    class Meta:
        verbose_name = "Уровень"
        verbose_name_plural = "Уровни"
        ordering = ["number"]

    def __str__(self) -> str:
        return f"Уровень {self.number}: {self.name_uz}"


class GameSession(models.Model):
    """Игровая сессия игрока (legacy — сохранена для совместимости)."""

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
    """Прогресс игрока по уровню (legacy — сохранена для совместимости)."""

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
    actions_performed = models.JSONField(default=dict, verbose_name="Выполненные действия")
    world_state = models.JSONField(default=dict, verbose_name="Состояние мира")
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


class Achievement(models.Model):
    """Определение достижения."""

    key = models.CharField(max_length=50, unique=True, verbose_name="Ключ")
    name_uz = models.CharField(max_length=100, verbose_name="Название (уз)")
    description_uz = models.TextField(verbose_name="Описание (уз)")
    icon = models.CharField(max_length=50, default="star", verbose_name="Иконка")
    condition_type = models.CharField(
        max_length=20, choices=ConditionType.choices, verbose_name="Тип условия"
    )
    condition_value = models.JSONField(default=dict, verbose_name="Значение условия")

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


# ─── Quiz Models ─────────────────────────────────────────────────────────────


class Question(models.Model):
    """Вопрос викторины."""

    text_uz = models.CharField(max_length=500, verbose_name="Вопрос (уз)")
    category = models.CharField(
        max_length=10, choices=ActionCategory.choices, verbose_name="Категория"
    )
    difficulty = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(3)],
        verbose_name="Сложность (1-3)",
    )
    question_type = models.CharField(
        max_length=10,
        choices=QuestionType.choices,
        default=QuestionType.MCQ,
        verbose_name="Тип вопроса",
    )
    explanation_uz = models.TextField(verbose_name="Пояснение (уз)")
    image = models.ImageField(
        upload_to="questions/",
        null=True,
        blank=True,
        verbose_name="Изображение",
    )
    time_limit = models.PositiveSmallIntegerField(default=30, verbose_name="Лимит времени (сек)")
    source = models.CharField(max_length=200, blank=True, verbose_name="Источник")
    related_article = models.ForeignKey(
        "education.EducationalContent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="questions",
        verbose_name="Связанная статья",
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ["category", "difficulty"]

    def __str__(self) -> str:
        short = self.text_uz[:60] + "..." if len(self.text_uz) > 60 else self.text_uz
        return f"[{self.category}] {short}"


class Answer(models.Model):
    """Вариант ответа на вопрос."""

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Вопрос",
    )
    text_uz = models.CharField(max_length=300, verbose_name="Ответ (уз)")
    is_correct = models.BooleanField(default=False, verbose_name="Правильный")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
        ordering = ["order"]

    def __str__(self) -> str:
        mark = "✓" if self.is_correct else "✗"
        return f"{mark} {self.text_uz[:50]}"


class QuizSession(models.Model):
    """Сессия викторины игрока."""

    player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quiz_sessions",
        verbose_name="Игрок",
    )
    mode = models.CharField(max_length=10, choices=QuizMode.choices, verbose_name="Режим")
    category = models.CharField(
        max_length=10,
        choices=ActionCategory.choices,
        null=True,
        blank=True,
        verbose_name="Категория",
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Начало")
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name="Конец")
    score = models.PositiveIntegerField(default=0, verbose_name="Очки")
    correct_count = models.PositiveIntegerField(default=0, verbose_name="Правильных ответов")
    total_questions = models.PositiveIntegerField(default=0, verbose_name="Всего вопросов")
    max_streak = models.PositiveIntegerField(default=0, verbose_name="Макс. серия")
    current_streak = models.PositiveIntegerField(default=0, verbose_name="Текущая серия")

    class Meta:
        verbose_name = "Сессия викторины"
        verbose_name_plural = "Сессии викторины"
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"{self.player} — {self.mode} ({self.score}pts)"


class QuizAnswer(models.Model):
    """Ответ игрока на конкретный вопрос викторины."""

    session = models.ForeignKey(
        QuizSession,
        on_delete=models.CASCADE,
        related_name="given_answers",
        verbose_name="Сессия",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name="Вопрос",
    )
    selected_answer = models.ForeignKey(
        Answer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Выбранный ответ",
    )
    is_correct = models.BooleanField(default=False, verbose_name="Правильно")
    time_spent_ms = models.PositiveIntegerField(default=0, verbose_name="Время ответа (мс)")
    answered_at = models.DateTimeField(auto_now_add=True, verbose_name="Время ответа")

    class Meta:
        verbose_name = "Ответ в викторине"
        verbose_name_plural = "Ответы в викторине"
        unique_together = ("session", "question")

    def __str__(self) -> str:
        mark = "✓" if self.is_correct else "✗"
        return f"{mark} {self.question} — {self.time_spent_ms}ms"


class DailyChallenge(models.Model):
    """Ежедневное задание с набором вопросов."""

    date = models.DateField(unique=True, verbose_name="Дата")
    questions = models.ManyToManyField(
        Question,
        related_name="daily_challenges",
        verbose_name="Вопросы",
    )
    bonus_score = models.PositiveIntegerField(default=50, verbose_name="Бонус (очки)")

    class Meta:
        verbose_name = "Ежедневное задание"
        verbose_name_plural = "Ежедневные задания"
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"Daily {self.date} (+{self.bonus_score}pts)"


class MiniGameScore(models.Model):
    """Результат мини-игры сортировки отходов."""

    GAME_TYPE_SORTING = "SORTING"
    GAME_TYPE_CHOICES = [(GAME_TYPE_SORTING, "Чiqindi saralash")]

    player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mini_game_scores",
        verbose_name="Игрок",
    )
    game_type = models.CharField(
        max_length=20,
        choices=GAME_TYPE_CHOICES,
        default=GAME_TYPE_SORTING,
        verbose_name="Тип игры",
    )
    score = models.PositiveIntegerField(default=0, verbose_name="Очки")
    correct_count = models.PositiveIntegerField(default=0, verbose_name="Правильных")
    total_items = models.PositiveIntegerField(default=0, verbose_name="Всего предметов")
    played_at = models.DateTimeField(auto_now_add=True, verbose_name="Сыграно")

    class Meta:
        verbose_name = "Результат мини-игры"
        verbose_name_plural = "Результаты мини-игры"
        ordering = ["-played_at"]

    def __str__(self) -> str:
        return f"{self.player} — {self.game_type}: {self.score}pts"
