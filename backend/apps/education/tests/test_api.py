import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.education.models import EcoFact, EducationalContent
from apps.game.models import ActionCategory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def articles(db):
    EducationalContent.objects.create(
        title_uz="Suv maqolasi", body_uz="body", category=ActionCategory.WATER, order=1
    )
    EducationalContent.objects.create(
        title_uz="O'simlik maqolasi", body_uz="body", category=ActionCategory.FLORA, order=2
    )
    EducationalContent.objects.create(
        title_uz="Chiqindi (draft)",
        body_uz="body",
        category=ActionCategory.WASTE,
        order=3,
        is_published=False,
    )


@pytest.fixture
def eco_fact(db):
    return EcoFact.objects.create(
        text_uz="Test ekofakt.", source="Test", category=ActionCategory.FLORA
    )


@pytest.mark.django_db
class TestEducationArticlesAPI:
    def test_list_published_only(self, api_client, articles):
        response = api_client.get(reverse("education-articles"))
        assert response.status_code == status.HTTP_200_OK
        titles = [a["title_uz"] for a in response.data["results"]]
        assert "Suv maqolasi" in titles
        assert "Chiqindi (draft)" not in titles

    def test_filter_by_category(self, api_client, articles):
        response = api_client.get(reverse("education-articles"), {"category": "WATER"})
        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        assert all(a["category"] == "WATER" for a in results)

    def test_detail_view(self, api_client, articles):
        content = EducationalContent.objects.filter(is_published=True).first()
        response = api_client.get(reverse("education-article-detail", kwargs={"pk": content.pk}))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title_uz"] == content.title_uz

    def test_detail_draft_returns_404(self, api_client, articles):
        draft = EducationalContent.objects.get(is_published=False)
        response = api_client.get(reverse("education-article-detail", kwargs={"pk": draft.pk}))
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestRandomFactAPI:
    def test_random_fact_returns_fact(self, api_client, eco_fact):
        response = api_client.get(reverse("education-random-fact"))
        assert response.status_code == status.HTTP_200_OK
        assert "text_uz" in response.data

    def test_random_fact_empty_db(self, api_client):
        response = api_client.get(reverse("education-random-fact"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {}
