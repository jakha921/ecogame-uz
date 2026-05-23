from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import (
    Achievement,
    ActionLog,
    EcoAction,
    GameProgress,
    GameSession,
    Level,
    PlayerAchievement,
)


@admin.register(Level)
class LevelAdmin(ModelAdmin):
    list_display = ["number", "name_uz", "required_score"]
    list_filter = ["number"]
    ordering = ["number"]


@admin.register(EcoAction)
class EcoActionAdmin(ModelAdmin):
    list_display = ["key", "name_uz", "category", "score_value", "unlock_level"]
    list_filter = ["category"]
    search_fields = ["key", "name_uz"]


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


@admin.register(ActionLog)
class ActionLogAdmin(ModelAdmin):
    list_display = ["session", "action", "performed_at"]
    list_filter = ["action__category"]
    date_hierarchy = "performed_at"


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
