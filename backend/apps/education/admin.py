from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import EcoFact, EducationalContent


@admin.register(EducationalContent)
class EducationalContentAdmin(ModelAdmin):
    list_display = ["title_uz", "category", "is_published", "order"]
    list_filter = ["category", "is_published"]
    list_editable = ["order", "is_published"]
    search_fields = ["title_uz"]
    ordering = ["order"]


@admin.register(EcoFact)
class EcoFactAdmin(ModelAdmin):
    list_display = ["text_uz", "category", "source"]
    list_filter = ["category"]
    search_fields = ["text_uz"]
