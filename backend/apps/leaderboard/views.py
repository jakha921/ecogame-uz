from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import LeaderboardEntry
from .serializers import LeaderboardEntrySerializer


class LeaderboardListView(generics.ListAPIView):
    serializer_class = LeaderboardEntrySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return LeaderboardEntry.objects.select_related("player").order_by("rank")[:50]


class PlayerRankView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            entry = LeaderboardEntry.objects.select_related("player").get(player=request.user)
            serializer = LeaderboardEntrySerializer(entry)
            return Response(serializer.data)
        except LeaderboardEntry.DoesNotExist:
            return Response({"detail": "Hali reyting yo'q."}, status=status.HTTP_404_NOT_FOUND)
