from rest_framework import serializers

from .models import LeaderboardEntry


class LeaderboardEntrySerializer(serializers.ModelSerializer):
    player_nickname = serializers.CharField(source="player.nickname", read_only=True)
    player_avatar = serializers.CharField(source="player.avatar", read_only=True)

    class Meta:
        model = LeaderboardEntry
        fields = [
            "rank",
            "player_nickname",
            "player_avatar",
            "total_score",
            "levels_completed",
            "achievements_count",
        ]
