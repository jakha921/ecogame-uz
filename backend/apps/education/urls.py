from django.urls import path

from .views import EducationalContentDetailView, EducationalContentListView, RandomEcoFactView

urlpatterns = [
    path("articles/", EducationalContentListView.as_view(), name="education-articles"),
    path(
        "articles/<int:pk>/",
        EducationalContentDetailView.as_view(),
        name="education-article-detail",
    ),
    path("facts/random/", RandomEcoFactView.as_view(), name="education-random-fact"),
]
