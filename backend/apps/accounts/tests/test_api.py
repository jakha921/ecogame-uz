import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

Player = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def player(db):
    return Player.objects.create_user(
        username="existinguser",
        nickname="ExistingNick",
        email="existing@example.com",
        password="securepass123",
    )


@pytest.fixture
def auth_client(api_client, player):
    response = api_client.post(
        reverse("auth-login"),
        {"username": "existinguser", "password": "securepass123"},
        format="json",
    )
    token = response.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client


@pytest.mark.django_db
class TestRegisterAPI:
    def test_register_success(self, api_client):
        response = api_client.post(
            reverse("auth-register"),
            {
                "username": "newuser",
                "nickname": "NewNick",
                "email": "new@example.com",
                "password": "securepass123",
                "password_confirm": "securepass123",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Player.objects.filter(username="newuser").exists()

    def test_register_password_mismatch(self, api_client):
        response = api_client.post(
            reverse("auth-register"),
            {
                "username": "mismatch",
                "nickname": "MismatchNick",
                "password": "securepass123",
                "password_confirm": "wrongpassword",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password_confirm" in response.data

    def test_register_duplicate_nickname(self, api_client, player):
        response = api_client.post(
            reverse("auth-register"),
            {
                "username": "otheruser",
                "nickname": "ExistingNick",
                "password": "securepass123",
                "password_confirm": "securepass123",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_short_password(self, api_client):
        response = api_client.post(
            reverse("auth-register"),
            {
                "username": "shortpass",
                "nickname": "ShortPassNick",
                "password": "short",
                "password_confirm": "short",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLoginAPI:
    def test_login_success(self, api_client, player):
        response = api_client.post(
            reverse("auth-login"),
            {"username": "existinguser", "password": "securepass123"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_wrong_password(self, api_client, player):
        response = api_client.post(
            reverse("auth-login"),
            {"username": "existinguser", "password": "wrongpassword"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_refresh(self, api_client, player):
        login_resp = api_client.post(
            reverse("auth-login"),
            {"username": "existinguser", "password": "securepass123"},
            format="json",
        )
        refresh_token = login_resp.data["refresh"]

        response = api_client.post(
            reverse("auth-token-refresh"),
            {"refresh": refresh_token},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data


@pytest.mark.django_db
class TestProfileAPI:
    def test_profile_get(self, auth_client, player):
        response = auth_client.get(reverse("auth-me"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "existinguser"
        assert response.data["nickname"] == "ExistingNick"
        assert "total_score" in response.data

    def test_profile_update_nickname(self, auth_client, player):
        response = auth_client.patch(
            reverse("auth-me"),
            {"nickname": "UpdatedNick"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        player.refresh_from_db()
        assert player.nickname == "UpdatedNick"

    def test_profile_update_avatar(self, auth_client, player):
        response = auth_client.patch(
            reverse("auth-me"),
            {"avatar": "fox"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        player.refresh_from_db()
        assert player.avatar == "fox"

    def test_profile_unauthorized(self, api_client):
        response = api_client.get(reverse("auth-me"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_profile_cannot_change_total_score(self, auth_client, player):
        response = auth_client.patch(
            reverse("auth-me"),
            {"total_score": 99999},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        player.refresh_from_db()
        assert player.total_score == 0


@pytest.mark.django_db
class TestAnonymousLogin:
    def test_creates_anonymous_player(self, api_client):
        response = api_client.post(reverse("auth-anonymous"), {}, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "access" in data
        assert "refresh" in data
        assert "session_key" in data
        assert data["is_anonymous"] is True

    def test_restores_existing_session(self, api_client):
        # First call creates a new anonymous player
        r1 = api_client.post(reverse("auth-anonymous"), {}, format="json")
        session_key = r1.json()["session_key"]

        # Second call with same session_key returns same account
        r2 = api_client.post(reverse("auth-anonymous"), {"session_key": session_key}, format="json")
        assert r2.status_code == status.HTTP_200_OK
        assert r2.json()["session_key"] == session_key
        # Only one anonymous player should exist for this session
        assert Player.objects.filter(session_key=session_key).count() == 1

    def test_unknown_session_key_creates_new_player(self, api_client):
        r = api_client.post(
            reverse("auth-anonymous"), {"session_key": "nonexistent_key"}, format="json"
        )
        assert r.status_code == status.HTTP_201_CREATED

    def test_anonymous_player_can_access_profile(self, api_client):
        r = api_client.post(reverse("auth-anonymous"), {}, format="json")
        token = r.json()["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        profile = api_client.get(reverse("auth-me"))
        assert profile.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestClaimAccount:
    def test_claim_converts_anonymous_to_real(self, api_client):
        # Create anonymous player
        r = api_client.post(reverse("auth-anonymous"), {}, format="json")
        token = r.json()["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # Claim the account
        claim = api_client.post(
            reverse("auth-claim"),
            {"username": "newuser", "nickname": "NewNick", "password": "pass12345"},
            format="json",
        )
        assert claim.status_code == status.HTTP_200_OK
        data = claim.json()
        assert data["username"] == "newuser"

        # Player is no longer anonymous
        p = Player.objects.get(username="newuser")
        assert p.is_anonymous_player is False
        assert p.session_key is None

    def test_claim_fails_for_registered_user(self, api_client, player):
        # Authenticate as a real (non-anonymous) player
        r = api_client.post(
            reverse("auth-login"),
            {"username": "existinguser", "password": "securepass123"},
            format="json",
        )
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {r.json()['access']}")

        claim = api_client.post(
            reverse("auth-claim"),
            {"username": "newuser", "nickname": "NewNick", "password": "pass12345"},
            format="json",
        )
        assert claim.status_code == status.HTTP_400_BAD_REQUEST
