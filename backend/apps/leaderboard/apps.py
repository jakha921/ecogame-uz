from django.apps import AppConfig


class LeaderboardConfig(AppConfig):
    name = "apps.leaderboard"
    verbose_name = "Лидерборд"

    def ready(self) -> None:
        import apps.leaderboard.signals  # noqa: F401
