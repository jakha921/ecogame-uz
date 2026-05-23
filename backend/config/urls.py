"""URL configuration for EcoGame project."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.accounts.urls")),
    # path("api/v1/game/", include("apps.game.urls")),
    # path("api/v1/education/", include("apps.education.urls")),
    # path("api/v1/leaderboard/", include("apps.leaderboard.urls")),
]
