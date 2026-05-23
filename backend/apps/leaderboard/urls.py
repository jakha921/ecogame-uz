from django.urls import path

from .views import LeaderboardListView, PlayerRankView

urlpatterns = [
    path("", LeaderboardListView.as_view(), name="leaderboard-list"),
    path("me/", PlayerRankView.as_view(), name="leaderboard-me"),
]
