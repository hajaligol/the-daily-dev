from django.db import models
from django.utils.text import slugify


class Article(models.Model):
    """A single newspaper-style article shown on the 'From Our Desk' page."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.CharField(
        max_length=100,
        help_text="Section label shown above the title, e.g. 'Developer Journal'.",
    )
    excerpt = models.TextField(
        help_text="Short teaser shown on the listing page."
    )
    image = models.ImageField(
        upload_to="articles/",
        verbose_name="Article image",
        help_text="Illustration shown alongside the article.",
    )
    image_alt = models.CharField(
        max_length=255,
        verbose_name="Article image alt text",
        help_text="Accessible description of the article image.",
    )
    page_reference = models.PositiveIntegerField(
        default=1,
        help_text="Page number shown in the 'Read more on page X' link.",
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Controls the position of the article in the listing (lower shows first).",
    )
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
