import secrets
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import PlayerSerializer, RegisterSerializer

Player = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class PlayerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch"]

    def get_object(self):
        return self.request.user


class AnonymousLoginView(APIView):
    """Создать анонимного игрока и вернуть JWT токены.

    Принимает опциональный session_key для восстановления существующей
    анонимной сессии (например, после перезагрузки страницы).
    """

    permission_classes = [AllowAny]

    def post(self, request):
        session_key = request.data.get("session_key") or ""

        if session_key:
            player = Player.objects.filter(
                session_key=session_key, is_anonymous_player=True
            ).first()
            if player:
                refresh = RefreshToken.for_user(player)
                return Response(
                    {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                        "session_key": session_key,
                        "is_anonymous": True,
                    }
                )

        # Create new anonymous player
        uid = uuid.uuid4().hex[:12]
        new_session_key = secrets.token_urlsafe(32)
        player = Player.objects.create_user(
            username=f"anon_{uid}",
            nickname=f"O'yinchi_{uid[:6]}",
            password=secrets.token_hex(16),
            is_anonymous_player=True,
            session_key=new_session_key,
        )

        refresh = RefreshToken.for_user(player)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "session_key": new_session_key,
                "is_anonymous": True,
            },
            status=status.HTTP_201_CREATED,
        )


class ClaimAccountView(APIView):
    """Привязать имя пользователя/пароль к анонимному аккаунту."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        player = request.user
        if not player.is_anonymous_player:
            return Response(
                {"detail": "Akkaunt allaqachon ro'yxatdan o'tgan."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        username = request.data.get("username", "").strip()
        nickname = request.data.get("nickname", "").strip()
        password = request.data.get("password", "")

        if not username or not password or not nickname:
            return Response(
                {"detail": "username, nickname va password talab qilinadi."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Player.objects.filter(username=username).exclude(pk=player.pk).exists():
            return Response({"detail": "Bu username band."}, status=status.HTTP_400_BAD_REQUEST)

        if Player.objects.filter(nickname=nickname).exclude(pk=player.pk).exists():
            return Response({"detail": "Bu nik band."}, status=status.HTTP_400_BAD_REQUEST)

        player.username = username
        player.nickname = nickname
        player.set_password(password)
        player.is_anonymous_player = False
        player.session_key = None
        player.save()

        return Response(PlayerSerializer(player).data)


class GoogleAuthView(APIView):
    """Аутентификация через Google ID token. Возвращает JWT токены."""

    permission_classes = [AllowAny]

    def post(self, request):
        credential = request.data.get("credential", "")
        if not credential:
            return Response(
                {"detail": "credential talab qilinadi."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payload = google_id_token.verify_oauth2_token(
                credential,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )
        except ValueError:
            return Response(
                {"detail": "Google token yaroqsiz."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        google_id = payload["sub"]
        email = payload.get("email", "")
        name = payload.get("name", "")

        # 1. Find by google_id
        player = Player.objects.filter(google_id=google_id).first()

        if not player:
            # 2. Find by email — link google_id
            player = Player.objects.filter(email=email).first()
            if player:
                player.google_id = google_id
                player.save(update_fields=["google_id"])
            else:
                # 3. Create new player
                uid = uuid.uuid4().hex[:8]
                nickname = name[:48] if name else f"Player_{uid}"
                base = nickname
                i = 1
                while Player.objects.filter(nickname=nickname).exists():
                    nickname = f"{base}_{i}"
                    i += 1
                player = Player.objects.create_user(
                    username=f"g_{google_id[:20]}",
                    email=email,
                    nickname=nickname,
                    password=secrets.token_hex(16),
                    google_id=google_id,
                )

        refresh = RefreshToken.for_user(player)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "is_new": player.last_login is None,
            }
        )
