from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import LeaderboardEntry


@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(ModelAdmin):
    list_display = [
        "rank",
        "player",
        "total_score",
        "levels_completed",
        "achievements_count",
        "updated_at",
    ]
    ordering = ["rank"]
    search_fields = ["player__username", "player__nickname"]
    readonly_fields = ["rank", "updated_at"]
