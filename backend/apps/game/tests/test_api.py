import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.game.models import EcoAction, GameSession, Level

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
def eco_action(db, level):
    return EcoAction.objects.create(
        key="api_test_action",
        name_uz="API harakat",
        description_uz="desc",
        category="FLORA",
        score_value=20,
        air_impact=1.0,
        water_impact=0.5,
        soil_impact=0.3,
        biodiversity_impact=0.8,
        cooldown_seconds=5,
        unlock_level=level,
        sprite_key="sprite",
    )


@pytest.mark.django_db
class TestLevelsAPI:
    def test_levels_list_public(self, api_client, level):
        response = api_client.get(reverse("level-list"))
        assert response.status_code == status.HTTP_200_OK
        numbers = [l["number"] for l in response.data["results"]]
        assert 77 in numbers

    def test_level_detail(self, api_client, level):
        response = api_client.get(reverse("level-detail", kwargs={"pk": level.pk}))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["number"] == 77

    def test_is_unlocked_for_authenticated(self, auth_client, level):
        response = auth_client.get(reverse("level-list"))
        assert response.status_code == status.HTTP_200_OK
        level_data = next(l for l in response.data["results"] if l["number"] == 77)
        assert level_data["is_unlocked"] is True


@pytest.mark.django_db
class TestSessionFlow:
    def test_start_session(self, auth_client, level):
        response = auth_client.post(
            reverse("session-start"),
            {"level_id": level.pk},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["is_active"] is True

    def test_start_session_locked_level(self, auth_client, db):
        locked = Level.objects.create(
            number=66,
            name_uz="Locked",
            description_uz="desc",
            required_score=9999,
            map_config={},
            ecosystem_initial={"air": 10, "water": 10, "soil": 10, "biodiversity": 10},
        )
        response = auth_client.post(
            reverse("session-start"),
            {"level_id": locked.pk},
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_submit_actions(self, auth_client, level, eco_action):
        start = auth_client.post(reverse("session-start"), {"level_id": level.pk}, format="json")
        session_id = start.data["id"]

        response = auth_client.post(
            reverse("session-actions", kwargs={"session_id": session_id}),
            {"actions": [{"action_key": "api_test_action", "position_x": 10, "position_y": 20}]},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["score"] == 20

    def test_end_session(self, auth_client, level):
        start = auth_client.post(reverse("session-start"), {"level_id": level.pk}, format="json")
        session_id = start.data["id"]

        response = auth_client.post(reverse("session-end", kwargs={"session_id": session_id}))
        assert response.status_code == status.HTTP_200_OK
        assert not GameSession.objects.get(pk=session_id).is_active


@pytest.mark.django_db
class TestProgressAPI:
    def test_progress_list(self, auth_client, level):
        auth_client.post(reverse("session-start"), {"level_id": level.pk}, format="json")
        response = auth_client.get(reverse("game-progress"))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1

    def test_progress_unauthorized(self, api_client):
        response = api_client.get(reverse("game-progress"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


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
        assert response.data["count"] == 0
