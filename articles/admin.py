from django.contrib import admin
from django.utils.html import format_html

from .models import Article, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "is_published",
        "image_preview",
        "updated_at",
    )
    list_display_links = ("title",)
    list_editable = ("is_published",)
    list_filter = ("is_published", "category")
    search_fields = ("title", "category__name", "excerpt", "topics__name")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "image_preview")
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Editorial",
            {
                "fields": ("title", "slug", "category", "excerpt", "is_published"),
            },
        ),
        (
            "Article body",
            {
                "fields": ("content", "topics"),
                "description": (
                    "Written as simple HTML (&lt;p&gt;, "
                    '&lt;h2 class="article-section-title"&gt;, '
                    '&lt;blockquote class="article-pullquote"&gt;, &lt;ul&gt;). '
                    "Include the token [[HERO_IMAGE:caption text]] once, at "
                    "the point where the article's own image should appear. "
                    "The body is sanitized to a fixed set of tags before "
                    "being rendered publicly."
                ),
            },
        ),
        (
            "Image",
            {"fields": ("image", "image_preview", "image_alt")},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    @admin.display(description="Preview")
    def image_preview(self, article):
        if not article.image:
            return "—"
        return format_html(
            '<img src="{}" alt="" style="max-height:60px;max-width:100px;'
            'object-fit:cover;border:1px solid #ccc;">',
            article.image.url,
        )
