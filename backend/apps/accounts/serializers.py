from django.contrib.auth import get_user_model
from rest_framework import serializers

Player = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = Player
        fields = ["username", "nickname", "email", "password", "password_confirm"]

    def validate_nickname(self, value: str) -> str:
        if Player.objects.filter(nickname=value).exists():
            raise serializers.ValidationError("Bu nik band. Boshqa nik tanlang.")
        return value

    def validate(self, attrs: dict) -> dict:
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "Parollar mos kelmadi."})
        return attrs

    def create(self, validated_data: dict) -> Player:
        return Player.objects.create_user(**validated_data)


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ["id", "username", "nickname", "email", "avatar", "total_score", "date_joined"]
        read_only_fields = ["id", "username", "total_score", "date_joined"]
