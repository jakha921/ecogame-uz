import pytest
from django.contrib.auth import get_user_model

from apps.game.models import Achievement, ConditionType, GameProgress, GameSession, Level
from apps.game.services import GameService

Player = get_user_model()


@pytest.fixture
def player(db):
    return Player.objects.create_user(username="svcuser", nickname="SvcNick", password="pass")


@pytest.fixture
def level(db):
    return Level.objects.create(
        number=88,
        name_uz="Service test daraja",
        description_uz="desc",
        required_score=0,
        map_config={},
        ecosystem_initial={"air": 30, "water": 25, "soil": 20, "biodiversity": 15},
    )


@pytest.mark.django_db
class TestStartSession:
    def test_creates_session(self, player, level):
        session = GameService.start_session(player, level)
        assert isinstance(session, GameSession)
        assert session.is_active
        assert session.player == player
        assert session.level == level

    def test_creates_progress_if_absent(self, player, level):
        GameService.start_session(player, level)
        assert GameProgress.objects.filter(player=player, level=level).exists()

    def test_progress_uses_ecosystem_initial(self, player, level):
        GameService.start_session(player, level)
        progress = GameProgress.objects.get(player=player, level=level)
        assert progress.air_quality == 30.0
        assert progress.water_purity == 25.0
        assert progress.soil_health == 20.0
        assert progress.biodiversity == 15.0

    def test_does_not_duplicate_progress(self, player, level):
        GameService.start_session(player, level)
        GameService.start_session(player, level)
        assert GameProgress.objects.filter(player=player, level=level).count() == 1


@pytest.mark.django_db
class TestAchievementUnlock:
    def test_score_achievement_unlocked(self, player, level):
        Achievement.objects.create(
            key="score_test_ach",
            name_uz="Yutuq",
            description_uz="desc",
            icon="star",
            condition_type=ConditionType.SCORE,
            condition_value={"min_score": 10},
        )
        progress = GameProgress.objects.create(player=player, level=level, score=100)
        unlocked = GameService.check_achievements(player, progress)
        keys = [a.key for a in unlocked]
        assert "score_test_ach" in keys

    def test_already_unlocked_not_returned(self, player, level):
        from apps.game.models import PlayerAchievement

        ach = Achievement.objects.create(
            key="already_unlocked",
            name_uz="Yutuq",
            description_uz="desc",
            icon="star",
            condition_type=ConditionType.SCORE,
            condition_value={"min_score": 0},
        )
        PlayerAchievement.objects.create(player=player, achievement=ach)
        progress = GameProgress.objects.create(player=player, level=level, score=999)
        unlocked = GameService.check_achievements(player, progress)
        keys = [a.key for a in unlocked]
        assert "already_unlocked" not in keys


@pytest.mark.django_db
class TestLevelCompletion:
    def test_complete_when_all_above_80(self, player, level):
        progress = GameProgress.objects.create(
            player=player,
            level=level,
            air_quality=80.0,
            water_purity=80.0,
            soil_health=80.0,
            biodiversity=80.0,
        )
        assert GameService.check_level_completion(progress) is True

    def test_incomplete_when_one_below_80(self, player, level):
        progress = GameProgress.objects.create(
            player=player,
            level=level,
            air_quality=80.0,
            water_purity=79.9,
            soil_health=80.0,
            biodiversity=80.0,
        )
        assert GameService.check_level_completion(progress) is False
