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
