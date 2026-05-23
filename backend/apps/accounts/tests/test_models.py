import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

Player = get_user_model()


@pytest.mark.django_db
class TestPlayerModel:
    def test_create_player(self):
        player = Player.objects.create_user(
            username="testuser",
            nickname="TestNick",
            password="securepass123",
        )
        assert player.pk is not None
        assert player.username == "testuser"
        assert player.nickname == "TestNick"

    def test_default_values(self):
        player = Player.objects.create_user(
            username="defaultuser",
            nickname="DefaultNick",
            password="securepass123",
        )
        assert player.total_score == 0
        assert player.avatar == "default"

    def test_str_returns_nickname(self):
        player = Player.objects.create_user(
            username="struser",
            nickname="MyNick",
            password="securepass123",
        )
        assert str(player) == "MyNick"

    def test_str_falls_back_to_username(self):
        player = Player.objects.create_user(
            username="fallbackuser",
            nickname="",
            password="securepass123",
        )
        # Nickname is empty string → __str__ should fall back to username
        player.nickname = ""
        player.save()
        assert str(player) == "fallbackuser"

    def test_nickname_unique(self):
        Player.objects.create_user(
            username="user1",
            nickname="UniqueNick",
            password="securepass123",
        )
        with pytest.raises(IntegrityError):
            Player.objects.create_user(
                username="user2",
                nickname="UniqueNick",
                password="securepass123",
            )

    def test_ordering_by_total_score_desc(self):
        Player.objects.create_user(
            username="low", nickname="LowScore", password="pass", total_score=10
        )
        Player.objects.create_user(
            username="high", nickname="HighScore", password="pass", total_score=500
        )
        Player.objects.create_user(
            username="mid", nickname="MidScore", password="pass", total_score=250
        )

        players = list(Player.objects.filter(username__in=["low", "high", "mid"]))
        scores = [p.total_score for p in players]
        assert scores == sorted(scores, reverse=True)
