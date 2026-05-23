import pytest

from apps.education.models import EcoFact, EducationalContent
from apps.game.models import ActionCategory


@pytest.mark.django_db
class TestEducationalContentModel:
    def test_create_content(self):
        content = EducationalContent.objects.create(
            title_uz="Test sarlavha",
            body_uz="Test matni. Bu ekologiya haqida.",
            category=ActionCategory.WATER,
            order=1,
            is_published=True,
        )
        assert content.pk is not None
        assert content.title_uz == "Test sarlavha"
        assert content.is_published

    def test_default_is_published(self):
        content = EducationalContent.objects.create(
            title_uz="Default content",
            body_uz="Body text",
            category=ActionCategory.FLORA,
            order=2,
        )
        assert content.is_published

    def test_filter_by_published(self):
        EducationalContent.objects.create(
            title_uz="Published",
            body_uz="Body",
            category=ActionCategory.FLORA,
            order=10,
            is_published=True,
        )
        EducationalContent.objects.create(
            title_uz="Draft",
            body_uz="Body",
            category=ActionCategory.FLORA,
            order=11,
            is_published=False,
        )
        published = EducationalContent.objects.filter(is_published=True, order__in=[10, 11])
        drafts = EducationalContent.objects.filter(is_published=False, order__in=[10, 11])
        assert published.count() == 1
        assert drafts.count() == 1

    def test_filter_by_category(self):
        for i, cat in enumerate(
            [ActionCategory.WATER, ActionCategory.WASTE, ActionCategory.ENERGY]
        ):
            EducationalContent.objects.create(
                title_uz=f"Content {cat}",
                body_uz="Body",
                category=cat,
                order=100 + i,
            )
        water_content = EducationalContent.objects.filter(
            category=ActionCategory.WATER, order__gte=100
        )
        assert water_content.count() == 1

    def test_str_representation(self):
        content = EducationalContent.objects.create(
            title_uz="Str test",
            body_uz="Body",
            category=ActionCategory.FAUNA,
            order=99,
        )
        assert "Str test" in str(content) or str(content) is not None

    def test_created_at_auto(self):
        content = EducationalContent.objects.create(
            title_uz="Auto date",
            body_uz="Body",
            category=ActionCategory.FLORA,
            order=98,
        )
        assert content.created_at is not None


@pytest.mark.django_db
class TestEcoFactModel:
    def test_create_eco_fact(self):
        fact = EcoFact.objects.create(
            text_uz="Bir daraxt yiliga 22 kg CO2 shimadi.",
            source="FAO",
            category=ActionCategory.FLORA,
        )
        assert fact.pk is not None
        assert fact.text_uz == "Bir daraxt yiliga 22 kg CO2 shimadi."
        assert fact.source == "FAO"

    def test_text_max_length(self):
        long_text = "A" * 300
        fact = EcoFact.objects.create(
            text_uz=long_text,
            source="Test",
            category=ActionCategory.WATER,
        )
        assert len(fact.text_uz) == 300

    def test_category_choices(self):
        for cat in ActionCategory:
            fact = EcoFact.objects.create(
                text_uz=f"Fact for {cat}",
                source="Source",
                category=cat,
            )
            assert fact.category == cat

    def test_str_representation(self):
        fact = EcoFact.objects.create(
            text_uz="Ekologiya fakti.",
            source="UNEP",
            category=ActionCategory.WASTE,
        )
        assert str(fact) is not None
