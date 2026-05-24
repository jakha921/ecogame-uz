from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import (
    Achievement,
    Answer,
    DailyChallenge,
    GameProgress,
    GameSession,
    Level,
    MiniGameScore,
    PlayerAchievement,
    Question,
    QuizSession,
)


@admin.register(Level)
class LevelAdmin(ModelAdmin):
    list_display = ["number", "name_uz", "required_score"]
    list_filter = ["number"]
    ordering = ["number"]


@admin.register(GameSession)
class GameSessionAdmin(ModelAdmin):
    list_display = ["player", "level", "started_at", "ended_at", "is_active"]
    list_filter = ["is_active", "level"]
    date_hierarchy = "started_at"


@admin.register(GameProgress)
class GameProgressAdmin(ModelAdmin):
    list_display = ["player", "level", "score", "completed", "updated_at"]
    list_filter = ["completed", "level"]
    search_fields = ["player__username", "player__nickname"]


@admin.register(Achievement)
class AchievementAdmin(ModelAdmin):
    list_display = ["key", "name_uz", "condition_type"]
    list_filter = ["condition_type"]
    search_fields = ["key", "name_uz"]


@admin.register(PlayerAchievement)
class PlayerAchievementAdmin(ModelAdmin):
    list_display = ["player", "achievement", "unlocked_at"]
    list_filter = ["achievement"]
    date_hierarchy = "unlocked_at"


# ─── Quiz Admin ───────────────────────────────────────────────────────────────


class AnswerInline(TabularInline):
    model = Answer
    extra = 4
    fields = ["text_uz", "is_correct", "order"]


@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_display = [
        "text_uz_short",
        "category",
        "difficulty",
        "question_type",
        "is_active",
        "created_at",
    ]
    list_filter = ["category", "difficulty", "question_type", "is_active"]
    search_fields = ["text_uz", "explanation_uz"]
    list_editable = ["is_active"]
    inlines = [AnswerInline]

    def text_uz_short(self, obj: Question) -> str:
        return obj.text_uz[:60] + "..." if len(obj.text_uz) > 60 else obj.text_uz

    text_uz_short.short_description = "Savol"


@admin.register(QuizSession)
class QuizSessionAdmin(ModelAdmin):
    list_display = [
        "player",
        "mode",
        "category",
        "score",
        "correct_count",
        "total_questions",
        "started_at",
        "finished_at",
    ]
    list_filter = ["mode", "category"]
    date_hierarchy = "started_at"
    readonly_fields = ["player", "started_at"]


@admin.register(DailyChallenge)
class DailyChallengeAdmin(ModelAdmin):
    list_display = ["date", "bonus_score", "question_count"]
    filter_horizontal = ["questions"]

    def question_count(self, obj: DailyChallenge) -> int:
        return obj.questions.count()

    question_count.short_description = "Savollar soni"


@admin.register(MiniGameScore)
class MiniGameScoreAdmin(ModelAdmin):
    list_display = ["player", "game_type", "score", "correct_count", "total_items", "played_at"]
    list_filter = ["game_type"]
    date_hierarchy = "played_at"
