import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from apps.game.models import (
    Achievement,
    ActionCategory,
    ConditionType,
    EcoAction,
    GameProgress,
    GameSession,
    Level,
    PlayerAchievement,
)

Player = get_user_model()


@pytest.fixture
def level():
    return Level.objects.create(
        number=99,
        name_uz="Test daraja",
        description_uz="Test tavsif",
        required_score=0,
        map_config={"width": 10, "height": 10, "zones": []},
        ecosystem_initial={"air": 30, "water": 25, "soil": 20, "biodiversity": 15},
    )


@pytest.fixture
def player():
    return Player.objects.create_user(
        username="gametestuser",
        nickname="GameTestNick",
        password="securepass123",
    )


@pytest.fixture
def eco_action(level):
    return EcoAction.objects.create(
        key="test_action_unique",
        name_uz="Test harakat",
        description_uz="Test tavsif",
        category=ActionCategory.FLORA,
        score_value=10,
        air_impact=1.0,
        water_impact=0.5,
        soil_impact=0.3,
        biodiversity_impact=0.8,
        cooldown_seconds=5,
        unlock_level=level,
        sprite_key="test_sprite",
    )


@pytest.mark.django_db
class TestLevelModel:
    def test_create_level(self, level):
        assert level.pk is not None
        assert level.number == 99
        assert level.name_uz == "Test daraja"

    def test_ecosystem_initial_json(self, level):
        assert level.ecosystem_initial["air"] == 30
        assert level.ecosystem_initial["water"] == 25
        assert level.ecosystem_initial["soil"] == 20
        assert level.ecosystem_initial["biodiversity"] == 15

    def test_str_representation(self, level):
        assert "99" in str(level) or "Test daraja" in str(level)

    def test_number_unique(self, level):
        with pytest.raises(IntegrityError):
            Level.objects.create(
                number=99,
                name_uz="Duplicate",
                description_uz="Duplicate",
                required_score=0,
                map_config={},
                ecosystem_initial={},
            )


@pytest.mark.django_db
class TestEcoActionModel:
    def test_create_eco_action(self, eco_action):
        assert eco_action.pk is not None
        assert eco_action.key == "test_action_unique"
        assert eco_action.category == ActionCategory.FLORA

    def test_impact_values(self, eco_action):
        assert eco_action.air_impact == 1.0
        assert eco_action.water_impact == 0.5
        assert eco_action.biodiversity_impact == 0.8

    def test_key_unique(self, eco_action, level):
        with pytest.raises(IntegrityError):
            EcoAction.objects.create(
                key="test_action_unique",
                name_uz="Duplicate",
                description_uz="Dup",
                category=ActionCategory.WATER,
                score_value=5,
                air_impact=0,
                water_impact=0,
                soil_impact=0,
                biodiversity_impact=0,
                cooldown_seconds=1,
                unlock_level=level,
                sprite_key="dup",
            )

    def test_category_choices(self, eco_action, level):
        for category in [
            ActionCategory.WATER,
            ActionCategory.WASTE,
            ActionCategory.ENERGY,
            ActionCategory.FAUNA,
        ]:
            action = EcoAction.objects.create(
                key=f"test_cat_{category}",
                name_uz=f"Cat {category}",
                description_uz="desc",
                category=category,
                score_value=5,
                air_impact=0,
                water_impact=0,
                soil_impact=0,
                biodiversity_impact=0,
                cooldown_seconds=1,
                unlock_level=level,
                sprite_key="sprite",
            )
            assert action.category == category


@pytest.mark.django_db
class TestGameProgressModel:
    def test_create_progress(self, player, level):
        progress = GameProgress.objects.create(
            player=player,
            level=level,
            score=0,
            air_quality=30.0,
            water_purity=25.0,
            soil_health=20.0,
            biodiversity=15.0,
        )
        assert progress.pk is not None
        assert not progress.completed

    def test_unique_together_player_level(self, player, level):
        GameProgress.objects.create(player=player, level=level)
        with pytest.raises(IntegrityError):
            GameProgress.objects.create(player=player, level=level)

    def test_actions_performed_json_default(self, player, level):
        progress = GameProgress.objects.create(player=player, level=level)
        assert isinstance(progress.actions_performed, dict)

    def test_completion_fields(self, player, level):
        from django.utils import timezone

        progress = GameProgress.objects.create(player=player, level=level)
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()

        refreshed = GameProgress.objects.get(pk=progress.pk)
        assert refreshed.completed
        assert refreshed.completed_at is not None


@pytest.mark.django_db
class TestAchievementModel:
    def test_create_achievement(self):
        ach = Achievement.objects.create(
            key="test_ach_unique",
            name_uz="Test yutuq",
            description_uz="Test tavsif",
            icon="star",
            condition_type=ConditionType.SCORE,
            condition_value={"min_score": 100},
        )
        assert ach.pk is not None
        assert ach.key == "test_ach_unique"

    def test_condition_types(self):
        for i, ctype in enumerate(
            [
                ConditionType.SCORE,
                ConditionType.ACTION_COUNT,
                ConditionType.LEVEL_COMPLETE,
                ConditionType.INDICATOR,
            ]
        ):
            ach = Achievement.objects.create(
                key=f"ctype_test_{i}",
                name_uz=f"Yutuq {i}",
                description_uz="desc",
                icon="icon",
                condition_type=ctype,
                condition_value={},
            )
            assert ach.condition_type == ctype


@pytest.mark.django_db
class TestPlayerAchievementModel:
    def test_create_player_achievement(self, player):
        ach = Achievement.objects.create(
            key="player_ach_test",
            name_uz="Yutuq",
            description_uz="desc",
            icon="icon",
            condition_type=ConditionType.SCORE,
            condition_value={"min_score": 10},
        )
        pa = PlayerAchievement.objects.create(player=player, achievement=ach)
        assert pa.pk is not None
        assert pa.unlocked_at is not None

    def test_unique_together_player_achievement(self, player):
        ach = Achievement.objects.create(
            key="unique_ach_test",
            name_uz="Yutuq",
            description_uz="desc",
            icon="icon",
            condition_type=ConditionType.SCORE,
            condition_value={"min_score": 10},
        )
        PlayerAchievement.objects.create(player=player, achievement=ach)
        with pytest.raises(IntegrityError):
            PlayerAchievement.objects.create(player=player, achievement=ach)


@pytest.mark.django_db
class TestGameSessionModel:
    def test_create_session(self, player, level):
        session = GameSession.objects.create(player=player, level=level)
        assert session.pk is not None
        assert session.is_active
        assert session.started_at is not None
        assert session.ended_at is None

    def test_session_str(self, player, level):
        session = GameSession.objects.create(player=player, level=level)
        assert str(session) is not None
