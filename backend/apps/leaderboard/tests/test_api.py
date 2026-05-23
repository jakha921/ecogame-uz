import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.game.models import GameProgress, Level
from apps.leaderboard.models import LeaderboardEntry

Player = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def player(db):
    return Player.objects.create_user(username="lbuser", nickname="LBNick", password="pass")


@pytest.fixture
def auth_client(api_client, player):
    api_client.force_authenticate(user=player)
    return api_client


@pytest.fixture
def level(db):
    return Level.objects.create(
        number=55,
        name_uz="LB test daraja",
        description_uz="desc",
        required_score=0,
        map_config={},
        ecosystem_initial={"air": 30, "water": 25, "soil": 20, "biodiversity": 15},
    )


@pytest.mark.django_db
class TestLeaderboardAPI:
    def test_leaderboard_public(self, api_client):
        response = api_client.get(reverse("leaderboard-list"))
        assert response.status_code == status.HTTP_200_OK

    def test_leaderboard_ordered_by_rank(self, api_client, level, db):
        for i in range(3):
            p = Player.objects.create_user(
                username=f"rankuser{i}", nickname=f"RankNick{i}", password="pass"
            )
            LeaderboardEntry.objects.create(player=p, total_score=100 - i * 10, rank=i + 1)

        response = api_client.get(reverse("leaderboard-list"))
        assert response.status_code == status.HTTP_200_OK
        ranks = [e["rank"] for e in response.data["results"]]
        assert ranks == sorted(ranks)

    def test_leaderboard_max_50(self, api_client, db):
        for i in range(60):
            p = Player.objects.create_user(
                username=f"bulk{i}", nickname=f"BulkNick{i}", password="pass"
            )
            LeaderboardEntry.objects.create(player=p, total_score=i, rank=60 - i)

        response = api_client.get(reverse("leaderboard-list"))
        assert len(response.data["results"]) <= 50


@pytest.mark.django_db
class TestPlayerRankAPI:
    def test_my_rank_not_found(self, auth_client):
        response = auth_client.get(reverse("leaderboard-me"))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_my_rank_after_progress(self, auth_client, player, level):
        # Signal creates LeaderboardEntry when GameProgress is saved
        GameProgress.objects.create(
            player=player,
            level=level,
            score=200,
            air_quality=30,
            water_purity=25,
            soil_health=20,
            biodiversity=15,
        )
        response = auth_client.get(reverse("leaderboard-me"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_score"] == 200

    def test_my_rank_unauthorized(self, api_client):
        response = api_client.get(reverse("leaderboard-me"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestLeaderboardSignal:
    def test_signal_creates_entry_on_progress(self, player, level):
        assert not LeaderboardEntry.objects.filter(player=player).exists()
        GameProgress.objects.create(player=player, level=level, score=100)
        assert LeaderboardEntry.objects.filter(player=player).exists()

    def test_signal_updates_total_score(self, player, level):
        level2 = Level.objects.create(
            number=44,
            name_uz="Level 44",
            description_uz="desc",
            required_score=0,
            map_config={},
            ecosystem_initial={"air": 30, "water": 25, "soil": 20, "biodiversity": 15},
        )
        GameProgress.objects.create(player=player, level=level, score=100)
        GameProgress.objects.create(player=player, level=level2, score=150)

        entry = LeaderboardEntry.objects.get(player=player)
        assert entry.total_score == 250
