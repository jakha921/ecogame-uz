from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Achievement, EcoAction, GameProgress, GameSession, Level, PlayerAchievement
from .serializers import (
    AchievementSerializer,
    ActionBatchSerializer,
    EcoActionSerializer,
    GameProgressSerializer,
    GameSessionSerializer,
    LevelSerializer,
    PlayerAchievementSerializer,
)
from .services import GameService


class LevelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Level.objects.all().order_by("number")
    serializer_class = LevelSerializer
    permission_classes = [AllowAny]


class EcoActionListView(generics.ListAPIView):
    serializer_class = EcoActionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = EcoAction.objects.select_related("unlock_level").all()
        level_number = self.request.query_params.get("level")
        if level_number:
            qs = qs.filter(unlock_level__number__lte=level_number)
        return qs


class GameProgressListView(generics.ListAPIView):
    serializer_class = GameProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GameProgress.objects.filter(player=self.request.user).select_related("level")


class SessionStartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        level_id = request.data.get("level_id")
        if not level_id:
            return Response(
                {"detail": "level_id talab qilinadi."}, status=status.HTTP_400_BAD_REQUEST
            )

        level = get_object_or_404(Level, pk=level_id)

        if request.user.total_score < level.required_score:
            return Response(
                {"detail": "Bu daraja hali ochilmagan."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Close any existing active session for this level
        GameSession.objects.filter(player=request.user, level=level, is_active=True).update(
            is_active=False
        )

        session = GameService.start_session(request.user, level)
        serializer = GameSessionSerializer(session, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SessionEndView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, session_id: int) -> Response:
        session = get_object_or_404(GameSession, pk=session_id, player=request.user, is_active=True)
        progress = GameService.end_session(session)
        serializer = GameProgressSerializer(progress, context={"request": request})
        return Response(serializer.data)


class ActionSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, session_id: int) -> Response:
        session = get_object_or_404(GameSession, pk=session_id, player=request.user, is_active=True)

        serializer = ActionBatchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        progress = GameService.perform_actions(session, serializer.validated_data["actions"])
        return Response(GameProgressSerializer(progress, context={"request": request}).data)


class AchievementListView(generics.ListAPIView):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [AllowAny]


class PlayerAchievementListView(generics.ListAPIView):
    serializer_class = PlayerAchievementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PlayerAchievement.objects.filter(player=self.request.user).select_related(
            "achievement"
        )
