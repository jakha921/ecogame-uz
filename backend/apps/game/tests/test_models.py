import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from apps.game.models import (
    Achievement,
    ActionCategory,
    Answer,
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
def level(db):
    return Level.objects.create(
        number=99,
        name_uz="Test daraja",
        description_uz="Test tavsif",
        required_score=0,
        map_config={"width": 10, "height": 10, "zones": []},
        ecosystem_initial={"air": 30, "water": 25, "soil": 20, "biodiversity": 15},
    )


@pytest.fixture
def player(db):
    return Player.objects.create_user(
        username="gametestuser",
        nickname="GameTestNick",
        password="securepass123",
    )


@pytest.fixture
def question(db):
    return Question.objects.create(
        text_uz="Test savoli?",
        category=ActionCategory.ENERGY,
        difficulty=1,
        question_type=QuestionType.MCQ,
        explanation_uz="Test izoh",
        time_limit=30,
    )


# ──────────────────────────────────────────────────────────
# Level model
# ──────────────────────────────────────────────────────────
@pytest.mark.django_db
class TestLevelModel:
    def test_create_level(self, level):
        assert level.pk is not None
        assert level.number == 99

    def test_ecosystem_initial_json(self, level):
        assert level.ecosystem_initial["air"] == 30

    def test_str_representation(self, level):
        assert str(level)

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


# ──────────────────────────────────────────────────────────
# Achievement model
# ──────────────────────────────────────────────────────────
@pytest.mark.django_db
class TestAchievementModel:
    def test_create_achievement(self):
        ach = Achievement.objects.create(
            key="test_ach_unique",
            name_uz="Test yutuq",
            description_uz="desc",
            icon="star",
            condition_type=ConditionType.SCORE,
            condition_value={"min_score": 100},
        )
        assert ach.pk is not None

    def test_quiz_condition_types(self):
        for i, ctype in enumerate(
            [ConditionType.QUIZ_COUNT, ConditionType.STREAK, ConditionType.DAILY_STREAK]
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

    def test_unique_together(self, player):
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


# ──────────────────────────────────────────────────────────
# GameProgress / GameSession (legacy, kept for backward compat)
# ──────────────────────────────────────────────────────────
@pytest.mark.django_db
class TestGameProgressModel:
    def test_create_progress(self, player, level):
        progress = GameProgress.objects.create(player=player, level=level)
        assert progress.pk is not None
        assert not progress.completed


@pytest.mark.django_db
class TestGameSessionModel:
    def test_create_session(self, player, level):
        session = GameSession.objects.create(player=player, level=level)
        assert session.pk is not None
        assert session.is_active


# ──────────────────────────────────────────────────────────
# Question model
# ──────────────────────────────────────────────────────────
@pytest.mark.django_db
class TestQuestionModel:
    def test_create_question(self, question):
        assert question.pk is not None
        assert question.is_active is True
        assert question.difficulty == 1

    def test_default_is_active(self):
        q = Question.objects.create(
            text_uz="Savol?",
            category=ActionCategory.WATER,
            difficulty=2,
            question_type=QuestionType.TRUE_FALSE,
            explanation_uz="Izoh",
        )
        assert q.is_active is True

    def test_difficulty_choices(self):
        for diff in [1, 2, 3]:
            q = Question.objects.create(
                text_uz=f"Savol {diff}",
                category=ActionCategory.FLORA,
                difficulty=diff,
                question_type=QuestionType.MCQ,
                explanation_uz="Izoh",
            )
            assert q.difficulty == diff

    def test_active_filter(self):
        Question.objects.create(
            text_uz="Aktiv savol",
            category=ActionCategory.WASTE,
            difficulty=1,
            question_type=QuestionType.MCQ,
            explanation_uz="izoh",
            is_active=True,
        )
        Question.objects.create(
            text_uz="Passiv savol",
            category=ActionCategory.WASTE,
            difficulty=1,
            question_type=QuestionType.MCQ,
            explanation_uz="izoh",
            is_active=False,
        )
        assert Question.objects.filter(is_active=True, category=ActionCategory.WASTE).count() >= 1
        assert Question.objects.filter(is_active=False, category=ActionCategory.WASTE).count() >= 1


@pytest.mark.django_db
class TestAnswerModel:
    def test_create_answer(self, question):
        ans = Answer.objects.create(
            question=question,
            text_uz="Javob A",
            is_correct=True,
            order=1,
        )
        assert ans.pk is not None
        assert ans.is_correct is True

    def test_order_field(self, question):
        for i in range(1, 5):
            Answer.objects.create(
                question=question, text_uz=f"Javob {i}", is_correct=(i == 1), order=i
            )
        answers = list(question.answers.order_by("order"))
        orders = [a.order for a in answers]
        assert orders == sorted(orders)

    def test_cascade_delete(self, question):
        Answer.objects.create(question=question, text_uz="Javob", is_correct=True, order=1)
        qpk = question.pk
        question.delete()
        assert Answer.objects.filter(question_id=qpk).count() == 0


# ──────────────────────────────────────────────────────────
# QuizSession model
# ──────────────────────────────────────────────────────────
@pytest.mark.django_db
class TestQuizSessionModel:
    def test_create_quick_session(self, player):
        session = QuizSession.objects.create(player=player, mode=QuizMode.QUICK, total_questions=10)
        assert session.pk is not None
        assert session.score == 0
        assert session.current_streak == 0
        assert session.max_streak == 0
        assert session.correct_count == 0

    def test_category_mode_stores_category(self, player):
        session = QuizSession.objects.create(
            player=player,
            mode=QuizMode.CATEGORY,
            category=ActionCategory.FLORA,
            total_questions=5,
        )
        assert session.category == ActionCategory.FLORA

    def test_marathon_mode(self, player):
        session = QuizSession.objects.create(player=player, mode=QuizMode.MARATHON)
        assert session.mode == QuizMode.MARATHON

    def test_finished_at_null_by_default(self, player):
        session = QuizSession.objects.create(player=player, mode=QuizMode.QUICK, total_questions=10)
        assert session.finished_at is None

    def test_str_representation(self, player):
        session = QuizSession.objects.create(player=player, mode=QuizMode.DAILY)
        assert str(session)
