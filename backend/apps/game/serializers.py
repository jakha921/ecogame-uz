from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Achievement, GameProgress, GameSession, Level, PlayerAchievement

Player = get_user_model()


class LevelSerializer(serializers.ModelSerializer):
    is_unlocked = serializers.SerializerMethodField()

    class Meta:
        model = Level
        fields = [
            "id",
            "number",
            "name_uz",
            "description_uz",
            "required_score",
            "map_config",
            "ecosystem_initial",
            "is_unlocked",
        ]

    def get_is_unlocked(self, obj: Level) -> bool:
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return obj.required_score == 0
        return request.user.total_score >= obj.required_score


class GameProgressSerializer(serializers.ModelSerializer):
    level = LevelSerializer(read_only=True)

    class Meta:
        model = GameProgress
        fields = [
            "id",
            "level",
            "score",
            "air_quality",
            "water_purity",
            "soil_health",
            "biodiversity",
            "actions_performed",
            "completed",
            "completed_at",
            "updated_at",
        ]
        read_only_fields = ["id", "level", "completed_at", "updated_at"]


class GameSessionSerializer(serializers.ModelSerializer):
    level_id = serializers.IntegerField(write_only=True)
    level = LevelSerializer(read_only=True)

    class Meta:
        model = GameSession
        fields = ["id", "level_id", "level", "started_at", "ended_at", "is_active"]
        read_only_fields = ["id", "started_at", "ended_at", "is_active", "level"]


class AchievementSerializer(serializers.ModelSerializer):
    is_unlocked = serializers.SerializerMethodField()

    class Meta:
        model = Achievement
        fields = ["id", "key", "name_uz", "description_uz", "icon", "condition_type", "is_unlocked"]

    def get_is_unlocked(self, obj: Achievement) -> bool:
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return PlayerAchievement.objects.filter(player=request.user, achievement=obj).exists()


class PlayerAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)

    class Meta:
        model = PlayerAchievement
        fields = ["id", "achievement", "unlocked_at"]
