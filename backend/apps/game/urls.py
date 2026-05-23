from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AchievementListView,
    ActionSubmitView,
    EcoActionListView,
    GameProgressListView,
    LevelViewSet,
    PlayerAchievementListView,
    SessionEndView,
    SessionStartView,
)

router = DefaultRouter()
router.register(r"levels", LevelViewSet, basename="level")

urlpatterns = [
    path("", include(router.urls)),
    path("actions/", EcoActionListView.as_view(), name="game-actions"),
    path("progress/", GameProgressListView.as_view(), name="game-progress"),
    path("sessions/start/", SessionStartView.as_view(), name="session-start"),
    path("sessions/<int:session_id>/end/", SessionEndView.as_view(), name="session-end"),
    path("sessions/<int:session_id>/actions/", ActionSubmitView.as_view(), name="session-actions"),
    path("achievements/", AchievementListView.as_view(), name="game-achievements"),
    path("achievements/my/", PlayerAchievementListView.as_view(), name="game-my-achievements"),
]
