from django.db import models

from apps.game.models import ActionCategory


class EducationalContent(models.Model):
    """Образовательные статьи об экологии Узбекистана на узбекском языке."""

    title_uz = models.CharField(max_length=200, verbose_name="Заголовок (уз)")
    body_uz = models.TextField(verbose_name="Текст (уз)")
    category = models.CharField(
        max_length=10, choices=ActionCategory.choices, verbose_name="Категория"
    )
    image = models.ImageField(
        upload_to="education/", blank=True, null=True, verbose_name="Изображение"
    )
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Порядок")
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        verbose_name = "Образовательная статья"
        verbose_name_plural = "Образовательные статьи"
        ordering = ["order"]

    def __str__(self) -> str:
        return self.title_uz


class EcoFact(models.Model):
    """Короткие экологические факты для загрузочного экрана."""

    text_uz = models.CharField(max_length=300, verbose_name="Текст (уз)")
    source = models.CharField(max_length=200, blank=True, verbose_name="Источник")
    category = models.CharField(
        max_length=10, choices=ActionCategory.choices, verbose_name="Категория"
    )

    class Meta:
        verbose_name = "Экофакт"
        verbose_name_plural = "Экофакты"

    def __str__(self) -> str:
        return self.text_uz[:80]
