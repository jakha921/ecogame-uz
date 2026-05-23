from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from unfold.admin import ModelAdmin

from .models import Player


@admin.register(Player)
class PlayerAdmin(ModelAdmin, UserAdmin):
    """Административная панель игроков."""

    list_display = ["username", "nickname", "email", "total_score", "date_joined", "is_active"]
    list_filter = ["is_active", "date_joined"]
    search_fields = ["username", "nickname", "email"]
    ordering = ["-total_score"]

    fieldsets = UserAdmin.fieldsets + (  # type: ignore[operator]
        ("Игровые данные", {"fields": ("nickname", "avatar", "total_score")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (  # type: ignore[operator]
        ("Игровые данные", {"fields": ("nickname", "avatar")}),
    )
