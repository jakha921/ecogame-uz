from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Achievement,
    ActionCategory,
    GameProgress,
    GameSession,
    Level,
    MiniGameScore,
    PlayerAchievement,
    Question,
    QuizSession,
)
from .serializers import (
    AchievementSerializer,
    DailyChallengeSerializer,
    GameProgressSerializer,
    GameSessionSerializer,
    LevelSerializer,
    MiniGameScoreSerializer,
    PlayerAchievementSerializer,
    QuestionSerializer,
    QuizSessionCreateSerializer,
    QuizSessionSerializer,
    SubmitAnswerSerializer,
)
from .services import GameService, QuizService

# ─── Legacy views (level list, session flow) ──────────────────────────────────


class LevelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Level.objects.all().order_by("number")
    serializer_class = LevelSerializer
    permission_classes = [permissions.AllowAny]


class GameProgressListView(generics.ListAPIView):
    serializer_class = GameProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GameProgress.objects.filter(player=self.request.user).select_related("level")


class SessionStartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        level_id = request.data.get("level_id")
        if not level_id:
            return Response(
                {"detail": "level_id talab qilinadi."}, status=status.HTTP_400_BAD_REQUEST
            )
        level = get_object_or_404(Level, pk=level_id)
        if request.user.total_score < level.required_score:
            return Response(
                {"detail": "Bu daraja hali ochilmagan."}, status=status.HTTP_403_FORBIDDEN
            )
        GameSession.objects.filter(player=request.user, level=level, is_active=True).update(
            is_active=False
        )
        session = GameService.start_session(request.user, level)
        return Response(
            GameSessionSerializer(session, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class SessionEndView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, session_id: int) -> Response:
        session = get_object_or_404(GameSession, pk=session_id, player=request.user, is_active=True)
        progress = GameService.end_session(session)
        return Response(GameProgressSerializer(progress, context={"request": request}).data)


# ─── Quiz views ───────────────────────────────────────────────────────────────


class QuestionListView(generics.ListAPIView):
    """GET /api/v1/game/quiz/questions/?category=X&difficulty=N&limit=20"""

    serializer_class = QuestionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Question.objects.filter(is_active=True).prefetch_related("answers")
        category = self.request.query_params.get("category")
        difficulty = self.request.query_params.get("difficulty")
        if category in ActionCategory.values:
            qs = qs.filter(category=category)
        if difficulty and difficulty.isdigit():
            qs = qs.filter(difficulty=int(difficulty))
        limit = self.request.query_params.get("limit", "20")
        limit = int(limit) if limit.isdigit() else 20
        return qs.order_by("?")[:limit]


class QuizSessionStartView(APIView):
    """POST /api/v1/game/quiz/sessions/ — start a new quiz session"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = QuizSessionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session, questions = QuizService.start_session(
            player=request.user,
            mode=serializer.validated_data["mode"],
            category=serializer.validated_data.get("category"),
        )
        data = QuizSessionSerializer(session).data
        data["questions"] = QuestionSerializer(questions, many=True).data
        return Response(data, status=status.HTTP_201_CREATED)


class QuizAnswerSubmitView(APIView):
    """POST /api/v1/game/quiz/sessions/{session_id}/answer/"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, session_id: int) -> Response:
        try:
            session = QuizSession.objects.get(
                pk=session_id, player=request.user, finished_at__isnull=True
            )
        except QuizSession.DoesNotExist:
            return Response(
                {"detail": "Session not found or already finished."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = SubmitAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = QuizService.submit_answer(
                session=session,
                question_id=serializer.validated_data["question_id"],
                answer_id=serializer.validated_data.get("answer_id"),
                time_spent_ms=serializer.validated_data["time_spent_ms"],
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)


class QuizSessionEndView(APIView):
    """POST /api/v1/game/quiz/sessions/{session_id}/end/"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, session_id: int) -> Response:
        try:
            session = QuizSession.objects.get(
                pk=session_id, player=request.user, finished_at__isnull=True
            )
        except QuizSession.DoesNotExist:
            return Response({"detail": "Session not found."}, status=status.HTTP_404_NOT_FOUND)
        result = QuizService.end_session(session)
        return Response(
            {
                "session": QuizSessionSerializer(result["session"]).data,
                "accuracy": result["accuracy"],
                "rank_title": result["rank_title"],
                "achievements_unlocked": AchievementSerializer(
                    result["achievements_unlocked"], many=True
                ).data,
            }
        )


class DailyChallengeView(APIView):
    """GET /api/v1/game/quiz/daily/"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        challenge = QuizService.get_daily_challenge()
        return Response(DailyChallengeSerializer(challenge, context={"request": request}).data)


class PlayerStatsView(APIView):
    """GET /api/v1/game/quiz/stats/"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response(QuizService.get_player_stats(request.user))


class MiniGameScoreView(APIView):
    """POST /api/v1/game/mini-game/sort/score/"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = MiniGameScoreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        score_obj = MiniGameScore.objects.create(
            player=request.user,
            game_type=MiniGameScore.GAME_TYPE_SORTING,
            **serializer.validated_data,
        )
        Player = request.user.__class__
        Player.objects.filter(pk=request.user.pk).update(
            total_score=Player.objects.get(pk=request.user.pk).total_score + score_obj.score
        )
        return Response(
            {"score": score_obj.score, "message": "Natija saqlandi!"},
            status=status.HTTP_201_CREATED,
        )


# ─── Achievement views ────────────────────────────────────────────────────────


class AchievementListView(generics.ListAPIView):
    serializer_class = AchievementSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Achievement.objects.all().order_by("condition_type", "key")
    pagination_class = None


class PlayerAchievementListView(generics.ListAPIView):
    serializer_class = PlayerAchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return (
            PlayerAchievement.objects.filter(player=self.request.user)
            .select_related("achievement")
            .order_by("-unlocked_at")
        )
