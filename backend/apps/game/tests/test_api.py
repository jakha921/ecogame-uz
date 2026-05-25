import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.game.models import (
    ActionCategory,
    Answer,
    Level,
    Question,
    QuestionType,
    QuizMode,
)

Player = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def player(db):
    return Player.objects.create_user(username="gameapi", nickname="GameAPI", password="pass")


@pytest.fixture
def auth_client(api_client, player):
    api_client.force_authenticate(user=player)
    return api_client


@pytest.fixture
def level(db):
    return Level.objects.create(
        number=77,
        name_uz="API test daraja",
        description_uz="desc",
        required_score=0,
        map_config={},
        ecosystem_initial={"air": 30, "water": 25, "soil": 20, "biodiversity": 15},
    )


@pytest.fixture
def questions(db):
    qs = []
    for i in range(12):
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
# Legacy level/session API (kept for backward compatibility)
# ──────────────────────────────────────────────────────────
@pytest.mark.django_db
class TestLevelsAPI:
    def test_levels_list_public(self, api_client, level):
        response = api_client.get(reverse("level-list"))
        assert response.status_code == status.HTTP_200_OK

    def test_level_detail(self, api_client, level):
        response = api_client.get(reverse("level-detail", kwargs={"pk": level.pk}))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["number"] == 77


@pytest.mark.django_db
class TestAchievementsAPI:
    def test_achievements_list_public(self, api_client):
        response = api_client.get(reverse("game-achievements"))
        assert response.status_code == status.HTTP_200_OK

    def test_my_achievements_requires_auth(self, api_client):
        response = api_client.get(reverse("game-my-achievements"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_my_achievements_empty(self, auth_client):
        response = auth_client.get(reverse("game-my-achievements"))
        assert response.status_code == status.HTTP_200_OK


# ──────────────────────────────────────────────────────────
# Quiz questions list
# ──────────────────────────────────────────────────────────
@pytest.mark.django_db
class TestQuizQuestionsAPI:
    def test_questions_list_public(self, api_client, questions):
        response = api_client.get(reverse("quiz-questions"))
        assert response.status_code == status.HTTP_200_OK

    def test_questions_include_answers(self, api_client, questions):
        response = api_client.get(reverse("quiz-questions"))
        assert response.status_code == status.HTTP_200_OK
        if response.data.get("results"):
            first = response.data["results"][0]
        else:
            first = response.data[0]
        assert "answers" in first


# ──────────────────────────────────────────────────────────
# Quiz session start
# ──────────────────────────────────────────────────────────
@pytest.mark.django_db
class TestQuizSessionAPI:
    def test_start_quick_session(self, auth_client, questions):
        response = auth_client.post(
            reverse("quiz-session-start"), {"mode": QuizMode.QUICK}, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "session_id" in response.data or "id" in response.data

    def test_start_unauthorized(self, api_client, questions):
        response = api_client.post(
            reverse("quiz-session-start"), {"mode": QuizMode.QUICK}, format="json"
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_start_invalid_mode(self, auth_client, questions):
        response = auth_client.post(
            reverse("quiz-session-start"), {"mode": "INVALID_MODE"}, format="json"
        )
        assert response.status_code in (
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    def test_start_category_mode(self, auth_client, questions):
        response = auth_client.post(
            reverse("quiz-session-start"),
            {"mode": QuizMode.CATEGORY, "category": ActionCategory.ENERGY},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED


# ──────────────────────────────────────────────────────────
# Submit answer
# ──────────────────────────────────────────────────────────
@pytest.mark.django_db
class TestSubmitAnswerAPI:
    def _start_session(self, auth_client, questions):
        resp = auth_client.post(
            reverse("quiz-session-start"), {"mode": QuizMode.QUICK}, format="json"
        )
        assert resp.status_code == status.HTTP_201_CREATED
        session_id = resp.data.get("session_id") or resp.data.get("id")
        first_question = resp.data["questions"][0]
        return session_id, first_question

    def _get_correct_answer_id(self, question_id):
        """Look up correct answer from DB — API correctly hides is_correct."""
        return Answer.objects.get(question_id=question_id, is_correct=True).pk

    def _get_wrong_answer_id(self, question_id):
        return Answer.objects.filter(question_id=question_id, is_correct=False).first().pk

    def test_correct_answer(self, auth_client, questions):
        session_id, q = self._start_session(auth_client, questions)
        correct_id = self._get_correct_answer_id(q["id"])
        resp = auth_client.post(
            reverse("quiz-answer", kwargs={"session_id": session_id}),
            {"question_id": q["id"], "answer_id": correct_id, "time_spent_ms": 5000},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["is_correct"] is True
        assert resp.data["points_earned"] > 0

    def test_wrong_answer(self, auth_client, questions):
        session_id, q = self._start_session(auth_client, questions)
        wrong_id = self._get_wrong_answer_id(q["id"])
        resp = auth_client.post(
            reverse("quiz-answer", kwargs={"session_id": session_id}),
            {"question_id": q["id"], "answer_id": wrong_id, "time_spent_ms": 5000},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["is_correct"] is False
        assert resp.data["points_earned"] == 0

    def test_duplicate_answer_rejected(self, auth_client, questions):
        session_id, q = self._start_session(auth_client, questions)
        correct_id = self._get_correct_answer_id(q["id"])
        payload = {"question_id": q["id"], "answer_id": correct_id, "time_spent_ms": 5000}
        auth_client.post(
            reverse("quiz-answer", kwargs={"session_id": session_id}), payload, format="json"
        )
        resp = auth_client.post(
            reverse("quiz-answer", kwargs={"session_id": session_id}), payload, format="json"
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_answer_requires_auth(self, api_client, questions):
        resp = api_client.post(
            reverse("quiz-answer", kwargs={"session_id": 999}),
            {"question_id": 1, "answer_id": 1, "time_spent_ms": 1000},
            format="json",
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# ──────────────────────────────────────────────────────────
# End session
# ──────────────────────────────────────────────────────────
@pytest.mark.django_db
class TestEndSessionAPI:
    def test_end_session_returns_results(self, auth_client, questions):
        start = auth_client.post(
            reverse("quiz-session-start"), {"mode": QuizMode.QUICK}, format="json"
        )
        session_id = start.data.get("session_id") or start.data.get("id")
        resp = auth_client.post(reverse("quiz-session-end", kwargs={"session_id": session_id}))
        assert resp.status_code == status.HTTP_200_OK
        assert "accuracy" in resp.data
        assert "rank_title" in resp.data

    def test_end_session_unauthorized(self, api_client):
        resp = api_client.post(reverse("quiz-session-end", kwargs={"session_id": 1}))
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# ──────────────────────────────────────────────────────────
# Daily challenge
# ──────────────────────────────────────────────────────────
@pytest.mark.django_db
class TestDailyChallengeAPI:
    def test_get_daily_challenge(self, auth_client, questions):
        resp = auth_client.get(reverse("quiz-daily"))
        assert resp.status_code == status.HTTP_200_OK
        assert "date" in resp.data

    def test_daily_requires_auth(self, api_client):
        resp = api_client.get(reverse("quiz-daily"))
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# ──────────────────────────────────────────────────────────
# Player stats
# ──────────────────────────────────────────────────────────
@pytest.mark.django_db
class TestPlayerStatsAPI:
    def test_stats_returns_data(self, auth_client, questions):
        resp = auth_client.get(reverse("quiz-stats"))
        assert resp.status_code == status.HTTP_200_OK
        assert "total_quizzes" in resp.data
        assert "accuracy_pct" in resp.data
        assert "rank_title" in resp.data

    def test_stats_requires_auth(self, api_client):
        resp = api_client.get(reverse("quiz-stats"))
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# ──────────────────────────────────────────────────────────
# Full quiz flow E2E
# ──────────────────────────────────────────────────────────
@pytest.mark.django_db
class TestFullQuizFlow:
    def test_start_answer_end(self, auth_client, questions):
        # 1. Start
        start = auth_client.post(
            reverse("quiz-session-start"), {"mode": QuizMode.QUICK}, format="json"
        )
        assert start.status_code == status.HTTP_201_CREATED
        session_id = start.data.get("session_id") or start.data.get("id")
        quiz_questions = start.data["questions"]

        # 2. Answer first 3 questions correctly (look up correct answer from DB)
        for q in quiz_questions[:3]:
            correct_id = Answer.objects.get(question_id=q["id"], is_correct=True).pk
            resp = auth_client.post(
                reverse("quiz-answer", kwargs={"session_id": session_id}),
                {"question_id": q["id"], "answer_id": correct_id, "time_spent_ms": 3000},
                format="json",
            )
            assert resp.status_code == status.HTTP_200_OK

        # 3. End session
        end = auth_client.post(reverse("quiz-session-end", kwargs={"session_id": session_id}))
        assert end.status_code == status.HTTP_200_OK
        assert end.data["accuracy"] > 0
        assert end.data["rank_title"]

        # 4. Verify stats updated
        stats = auth_client.get(reverse("quiz-stats"))
        assert stats.status_code == status.HTTP_200_OK
        assert stats.data["total_quizzes"] >= 1
