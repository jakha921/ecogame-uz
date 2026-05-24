import random

from rest_framework import serializers

from .models import (
    Achievement,
    ActionCategory,
    Answer,
    DailyChallenge,
    GameProgress,
    GameSession,
    Level,
    PlayerAchievement,
    Question,
    QuizMode,
    QuizSession,
)

# ─── Legacy serializers (kept for backward-compat) ────────────────────────────


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


# ─── Quiz serializers ─────────────────────────────────────────────────────────


class AnswerSerializer(serializers.ModelSerializer):
    """Answer without is_correct — safe to send to the client before answering."""

    class Meta:
        model = Answer
        fields = ["id", "text_uz", "order"]


class AnswerWithCorrectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "text_uz", "order", "is_correct"]


class QuestionSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "id",
            "text_uz",
            "category",
            "difficulty",
            "question_type",
            "image",
            "time_limit",
            "source",
            "answers",
        ]

    def get_answers(self, obj: Question) -> list:
        answers = list(obj.answers.all())
        random.shuffle(answers)
        return AnswerSerializer(answers, many=True).data


class QuizSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizSession
        fields = [
            "id",
            "mode",
            "category",
            "started_at",
            "finished_at",
            "score",
            "correct_count",
            "total_questions",
            "max_streak",
        ]


class QuizSessionCreateSerializer(serializers.Serializer):
    mode = serializers.ChoiceField(choices=QuizMode.choices)
    category = serializers.ChoiceField(
        choices=ActionCategory.choices, required=False, allow_null=True
    )

    def validate(self, data: dict) -> dict:
        if data.get("mode") == "CATEGORY" and not data.get("category"):
            raise serializers.ValidationError({"category": "Category mode requires a category."})
        return data


class SubmitAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer_id = serializers.IntegerField(required=False, allow_null=True)
    time_spent_ms = serializers.IntegerField(min_value=0, max_value=120000)


class DailyChallengeSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = DailyChallenge
        fields = ["id", "date", "questions", "bonus_score", "is_completed"]

    def get_is_completed(self, obj: DailyChallenge) -> bool:
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return QuizSession.objects.filter(
            player=request.user,
            mode="DAILY",
            started_at__date=obj.date,
            finished_at__isnull=False,
        ).exists()


class MiniGameScoreSerializer(serializers.Serializer):
    score = serializers.IntegerField(min_value=0)
    correct_count = serializers.IntegerField(min_value=0)
    total_items = serializers.IntegerField(min_value=1)


# ─── Achievement serializers ──────────────────────────────────────────────────


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ["id", "key", "name_uz", "description_uz", "icon"]


class PlayerAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)

    class Meta:
        model = PlayerAchievement
        fields = ["id", "achievement", "unlocked_at"]
