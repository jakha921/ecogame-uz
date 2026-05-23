from rest_framework import serializers

from .models import EcoFact, EducationalContent


class EducationalContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationalContent
        fields = ["id", "title_uz", "body_uz", "category", "image", "order"]


class EcoFactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EcoFact
        fields = ["id", "text_uz", "source", "category"]
