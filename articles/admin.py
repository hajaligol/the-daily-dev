from django.contrib import admin

from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "order", "page_reference", "is_published", "created_at")
    list_filter = ("is_published", "category")
    search_fields = ("title", "category", "excerpt")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("order", "-created_at")
