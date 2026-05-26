import pytest
from django.contrib.auth import get_user_model

from apps.game.models import (
    Achievement,
    ActionCategory,
    Answer,
    ConditionType,
    PlayerAchievement,
    Question,
    QuestionType,
    QuizMode,
    QuizSession,
)
from apps.game.services import QuizService

Player = get_user_model()


@pytest.fixture
def player(db):
    return Player.objects.create_user(username="svcuser", nickname="SvcNick", password="pass")


@pytest.fixture
def question(db):
    q = Question.objects.create(
        text_uz="Test savoli?",
        category=ActionCategory.ENERGY,
        difficulty=1,
        question_type=QuestionType.MCQ,
        explanation_uz="Test izoh",
        time_limit=30,
    )
    Answer.objects.create(question=q, text_uz="To'g'ri javob", is_correct=True, order=1)
    Answer.objects.create(question=q, text_uz="Noto'g'ri javob", is_correct=False, order=2)
    return q


@pytest.fixture
def questions_bulk(db):
    """Create 15 questions across categories for mode tests."""
    qs = []
    for i in range(15):
        cat = ActionCategory.values[i % len(ActionCategory.values)]
        q = Question.objects.create(
            text_uz=f"Savol {i}",
            category=cat,
            difficulty=(i % 3) + 1,
            question_type=QuestionType.MCQ,
            explanation_uz=f"Izoh {i}",
            time_limit=30,
        )
        Answer.objects.create(question=q, text_uz="To'g'ri", is_correct=True, order=1)
        Answer.objects.create(question=q, text_uz="Noto'g'ri", is_correct=False, order=2)
        qs.append(q)
    return qs


# ──────────────────────────────────────────────────────────
# calculate_score
# ──────────────────────────────────────────────────────────
class TestCalculateScore:
    def test_incorrect_returns_zero(self):
        assert QuizService.calculate_score(False, 5000, 30, 0) == 0

    def test_correct_streak_0_no_time_bonus(self):
        # streak=0, answer at last millisecond → time_ratio≈0, factor=1.0
        score = QuizService.calculate_score(True, 30_000, 30, 0)
        assert score == 100

    def test_correct_streak_0_full_time_bonus(self):
        # Answered instantly → time_ratio=1.0, factor=1.5
        score = QuizService.calculate_score(True, 0, 30, 0)
        assert score == 150

    def test_streak_2_multiplier(self):
        # streak=2 → multiplier=1.5
        score = QuizService.calculate_score(True, 30_000, 30, 2)
        assert score == 150  # 100 * 1.5 * 1.0

    def test_streak_3_multiplier(self):
        # streak=3 → multiplier=2.0
        score = QuizService.calculate_score(True, 30_000, 30, 3)
        assert score == 200

    def test_streak_4_plus_max_multiplier(self):
        # streak≥4 → multiplier=3.0
        score = QuizService.calculate_score(True, 30_000, 30, 5)
        assert score == 300

    def test_score_always_non_negative(self):
        score = QuizService.calculate_score(True, 999_999, 30, 0)
        assert score >= 0


# ──────────────────────────────────────────────────────────
# get_rank_title
# ──────────────────────────────────────────────────────────
class TestGetRankTitle:
    def test_zero_score(self):
        assert QuizService.get_rank_title(0) == "Yangi o'quvchi"

    def test_below_100(self):
        assert QuizService.get_rank_title(99) == "Yangi o'quvchi"

    def test_exactly_100(self):
        assert QuizService.get_rank_title(100) == "Ekologik talaba"

    def test_exactly_500(self):
        assert QuizService.get_rank_title(500) == "Tabiat do'sti"

    def test_exactly_1500(self):
        assert QuizService.get_rank_title(1500) == "Eko-mutaxassis"

    def test_exactly_3000(self):
        assert QuizService.get_rank_title(3000) == "Eko-qahramon"

    def test_exactly_5000(self):
        assert QuizService.get_rank_title(5000) == "Eko-ustoz"

    def test_above_5000(self):
        assert QuizService.get_rank_title(9999) == "Eko-ustoz"


# ──────────────────────────────────────────────────────────
# start_session
# ──────────────────────────────────────────────────────────
@pytest.mark.django_db
class TestStartSession:
    def test_quick_mode_returns_10_questions(self, player, questions_bulk):
        session, questions = QuizService.start_session(player, QuizMode.QUICK)
        assert isinstance(session, QuizSession)
        assert len(questions) == 10

    def test_quick_mode_total_questions_set(self, player, questions_bulk):
        session, questions = QuizService.start_session(player, QuizMode.QUICK)
        assert session.total_questions == len(questions)

    def test_category_mode_filters_category(self, player, questions_bulk):
        session, questions = QuizService.start_session(
            player, QuizMode.CATEGORY, category=ActionCategory.ENERGY
        )
        for q in questions:
            assert q.category == ActionCategory.ENERGY

    def test_marathon_max_100(self, player, questions_bulk):
        session, questions = QuizService.start_session(player, QuizMode.MARATHON)
        assert len(questions) <= 100

    def test_session_mode_stored(self, player, questions_bulk):
        session, _ = QuizService.start_session(player, QuizMode.QUICK)
        assert session.mode == QuizMode.QUICK


# ──────────────────────────────────────────────────────────
# submit_answer
# ──────────────────────────────────────────────────────────
@pytest.mark.django_db
class TestSubmitAnswer:
    def test_correct_answer_increases_streak(self, player, question):
        session = QuizSession.objects.create(player=player, mode=QuizMode.QUICK, total_questions=5)
        correct = question.answers.get(is_correct=True)
        result = QuizService.submit_answer(session, question.pk, correct.pk, 5000)
        assert result["is_correct"] is True
        session.refresh_from_db()
        assert session.current_streak == 1

    def test_wrong_answer_resets_streak(self, player, question):
        session = QuizSession.objects.create(
            player=player, mode=QuizMode.QUICK, total_questions=5, current_streak=3
        )
        wrong = question.answers.get(is_correct=False)
        result = QuizService.submit_answer(session, question.pk, wrong.pk, 5000)
        assert result["is_correct"] is False
        session.refresh_from_db()
        assert session.current_streak == 0

    def test_correct_earns_points(self, player, question):
        session = QuizSession.objects.create(player=player, mode=QuizMode.QUICK, total_questions=5)
        correct = question.answers.get(is_correct=True)
        result = QuizService.submit_answer(session, question.pk, correct.pk, 5000)
        assert result["points_earned"] > 0

    def test_duplicate_answer_raises(self, player, question):
        session = QuizSession.objects.create(player=player, mode=QuizMode.QUICK, total_questions=5)
        correct = question.answers.get(is_correct=True)
        QuizService.submit_answer(session, question.pk, correct.pk, 5000)
        with pytest.raises(ValueError, match="Already answered"):
            QuizService.submit_answer(session, question.pk, correct.pk, 5000)

    def test_marathon_wrong_sets_game_over(self, player, question):
        session = QuizSession.objects.create(player=player, mode=QuizMode.MARATHON)
        wrong = question.answers.get(is_correct=False)
        result = QuizService.submit_answer(session, question.pk, wrong.pk, 5000)
        assert result["is_game_over"] is True

    def test_quick_wrong_not_game_over(self, player, question):
        session = QuizSession.objects.create(player=player, mode=QuizMode.QUICK, total_questions=5)
        wrong = question.answers.get(is_correct=False)
        result = QuizService.submit_answer(session, question.pk, wrong.pk, 5000)
        assert result["is_game_over"] is False


# ──────────────────────────────────────────────────────────
# end_session
# ──────────────────────────────────────────────────────────
@pytest.mark.django_db
class TestEndSession:
    def test_sets_finished_at(self, player):
        session = QuizSession.objects.create(player=player, mode=QuizMode.QUICK, total_questions=5)
        QuizService.end_session(session)
        session.refresh_from_db()
        assert session.finished_at is not None

    def test_accuracy_all_correct(self, player):
        session = QuizSession.objects.create(
            player=player, mode=QuizMode.QUICK, total_questions=10, correct_count=10
        )
        result = QuizService.end_session(session)
        assert result["accuracy"] == 1.0

    def test_accuracy_none_correct(self, player):
        session = QuizSession.objects.create(
            player=player, mode=QuizMode.QUICK, total_questions=10, correct_count=0
        )
        result = QuizService.end_session(session)
        assert result["accuracy"] == 0.0

    def test_rank_title_in_result(self, player):
        session = QuizSession.objects.create(player=player, mode=QuizMode.QUICK, total_questions=5)
        result = QuizService.end_session(session)
        assert "rank_title" in result

    def test_updates_player_total_score(self, player):
        session = QuizSession.objects.create(
            player=player, mode=QuizMode.QUICK, total_questions=5, score=500, correct_count=5
        )
        QuizService.end_session(session)
        player.refresh_from_db()
        assert player.total_score >= 500


# ──────────────────────────────────────────────────────────
# get_daily_challenge
# ──────────────────────────────────────────────────────────
@pytest.mark.django_db
class TestDailyChallenge:
    def test_creates_challenge(self, questions_bulk):
        from datetime import date

        challenge = QuizService.get_daily_challenge(date(2030, 1, 1))
        assert challenge.pk is not None

    def test_same_date_returns_same(self, questions_bulk):
        from datetime import date

        ch1 = QuizService.get_daily_challenge(date(2030, 2, 1))
        ch2 = QuizService.get_daily_challenge(date(2030, 2, 1))
        assert ch1.pk == ch2.pk

    def test_different_dates_different_challenges(self, questions_bulk):
        from datetime import date

        ch1 = QuizService.get_daily_challenge(date(2030, 3, 1))
        ch2 = QuizService.get_daily_challenge(date(2030, 3, 2))
        assert ch1.pk != ch2.pk


# ──────────────────────────────────────────────────────────
# check_quiz_achievements
# ──────────────────────────────────────────────────────────
@pytest.mark.django_db
class TestCheckAchievements:
    def test_score_threshold_unlocked(self, player):
        Achievement.objects.create(
            key="score_500_test",
            name_uz="Yutuq",
            description_uz="desc",
            icon="star",
            condition_type=ConditionType.SCORE,
            condition_value={"min_score": 500},
        )
        session = QuizSession.objects.create(
            player=player,
            mode=QuizMode.QUICK,
            total_questions=5,
            score=600,
            correct_count=5,
        )
        QuizService.end_session(session)
        player.refresh_from_db()
        player.__class__.objects.filter(pk=player.pk).update(total_score=600)
        player.refresh_from_db()

        session2 = QuizSession.objects.create(
            player=player, mode=QuizMode.QUICK, total_questions=1, score=0, correct_count=0
        )
        unlocked = QuizService.check_quiz_achievements(player, session2)
        keys = [a.key for a in unlocked]
        assert "score_500_test" in keys

    def test_quiz_count_threshold(self, player):
        # Achievement is unlocked inside end_session — verify via PlayerAchievement
        ach = Achievement.objects.create(
            key="quiz_count_2_test",
            name_uz="Yutuq",
            description_uz="desc",
            icon="trophy",
            condition_type=ConditionType.QUIZ_COUNT,
            condition_value={"count": 2},
        )
        for _ in range(2):
            s = QuizSession.objects.create(player=player, mode=QuizMode.QUICK, total_questions=5)
            QuizService.end_session(s)

        assert PlayerAchievement.objects.filter(player=player, achievement=ach).exists()

    def test_already_unlocked_not_returned(self, player):
        ach = Achievement.objects.create(
            key="already_done",
            name_uz="Yutuq",
            description_uz="desc",
            icon="star",
            condition_type=ConditionType.SCORE,
            condition_value={"min_score": 0},
        )
        PlayerAchievement.objects.create(player=player, achievement=ach)
        player.__class__.objects.filter(pk=player.pk).update(total_score=999)
        player.refresh_from_db()
        session = QuizSession.objects.create(player=player, mode=QuizMode.QUICK, total_questions=5)
        unlocked = QuizService.check_quiz_achievements(player, session)
        keys = [a.key for a in unlocked]
        assert "already_done" not in keys
