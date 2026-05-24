import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from apps.game.models import (
    Achievement,
    ActionCategory,
    ConditionType,
    GameProgress,
    GameSession,
    Level,
    PlayerAchievement,
    Question,
    QuestionType,
    QuizMode,
    QuizSession,
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
                ConditionType.QUIZ_COUNT,
                ConditionType.STREAK,
                ConditionType.DAILY_STREAK,
                ConditionType.CATEGORY_MASTER,
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


@pytest.mark.django_db
class TestQuestionModel:
    def test_create_question(self):
        q = Question.objects.create(
            text_uz="O'zbekistonda eng ko'p uchraydigan daraxt?",
            category=ActionCategory.FLORA,
            difficulty=1,
            question_type=QuestionType.MCQ,
            explanation_uz="Tut daraxti O'zbekistonda keng tarqalgan.",
            time_limit=30,
        )
        assert q.pk is not None
        assert q.is_active is True
        assert q.difficulty == 1

    def test_question_str(self):
        q = Question.objects.create(
            text_uz="Test savol?",
            category=ActionCategory.WATER,
            difficulty=2,
            question_type=QuestionType.TRUE_FALSE,
            explanation_uz="Izoh",
        )
        assert "WATER" in str(q) or "savol" in str(q).lower() or "Test" in str(q)

    def test_difficulty_choices(self):
        for diff in [1, 2, 3]:
            q = Question.objects.create(
                text_uz=f"Savol {diff}",
                category=ActionCategory.ENERGY,
                difficulty=diff,
                question_type=QuestionType.MCQ,
                explanation_uz="Izoh",
            )
            assert q.difficulty == diff


@pytest.mark.django_db
class TestQuizSessionModel:
    def test_create_quiz_session(self, player):
        session = QuizSession.objects.create(
            player=player,
            mode=QuizMode.QUICK,
            total_questions=10,
        )
        assert session.pk is not None
        assert session.score == 0
        assert session.current_streak == 0
        assert session.max_streak == 0

    def test_category_mode(self, player):
        session = QuizSession.objects.create(
            player=player,
            mode=QuizMode.CATEGORY,
            category=ActionCategory.FLORA,
            total_questions=5,
        )
        assert session.category == ActionCategory.FLORA

    def test_str_representation(self, player):
        session = QuizSession.objects.create(player=player, mode=QuizMode.MARATHON)
        assert "MARATHON" in str(session) or str(session)
