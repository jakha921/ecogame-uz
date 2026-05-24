from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"levels", views.LevelViewSet, basename="level")

urlpatterns = [
    # Legacy level + session endpoints (used by existing frontend)
    path("", include(router.urls)),
    path("progress/", views.GameProgressListView.as_view(), name="game-progress"),
    path("sessions/start/", views.SessionStartView.as_view(), name="session-start"),
    path("sessions/<int:session_id>/end/", views.SessionEndView.as_view(), name="session-end"),
    # Quiz endpoints
    path("quiz/questions/", views.QuestionListView.as_view(), name="quiz-questions"),
    path("quiz/sessions/", views.QuizSessionStartView.as_view(), name="quiz-session-start"),
    path(
        "quiz/sessions/<int:session_id>/answer/",
        views.QuizAnswerSubmitView.as_view(),
        name="quiz-answer",
    ),
    path(
        "quiz/sessions/<int:session_id>/end/",
        views.QuizSessionEndView.as_view(),
        name="quiz-session-end",
    ),
    path("quiz/daily/", views.DailyChallengeView.as_view(), name="quiz-daily"),
    path("quiz/stats/", views.PlayerStatsView.as_view(), name="quiz-stats"),
    # Mini-game
    path("mini-game/sort/score/", views.MiniGameScoreView.as_view(), name="mini-game-sort"),
    # Achievements
    path("achievements/", views.AchievementListView.as_view(), name="game-achievements"),
    path(
        "achievements/my/", views.PlayerAchievementListView.as_view(), name="game-my-achievements"
    ),
]
