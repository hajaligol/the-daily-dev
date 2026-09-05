import re

from django.db import models
from django.utils.html import strip_tags
from django.utils.text import slugify

# Marker used inside `Article.content` to say "the hero image + caption goes
# here". The template no longer uses this to position the image inline —
# the image is always rendered above the article text — but it still marks
# where the caption text comes from, and gets stripped out of the rendered
# body so it never appears as literal text.
HERO_IMAGE_TOKEN = re.compile(r"\[\[HERO_IMAGE:(.*?)\]\]", re.S)

# Matches the "<h2 ...>...</h2>" section headings inside `Article.content` so
# the "On This Page" side index can be generated from the real article body
# instead of being maintained as a second, easily-out-of-sync list.
SECTION_HEADING = re.compile(r"<h2[^>]*>(.*?)</h2>", re.I | re.S)


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
    content = models.TextField(
        blank=True,
        default="",
        help_text=(
            "Full article body shown on the detail page. Written as simple "
            "HTML (<p>, <h2 class=\"article-section-title\">, <blockquote "
            "class=\"article-pullquote\">, <ul>) and rendered as-is, the way "
            "a newsroom CMS body field would be. Include the token "
            "'[[HERO_IMAGE:caption text]]' once, at the point where the "
            "article's own image should appear."
        ),
    )
    topics = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text=(
            "Optional comma-separated topic tags shown in the side column, "
            "e.g. 'Mindset, Debugging, Logs, Growth'."
        ),
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

    # ------------------------------------------------------------------
    # Detail-page helpers
    # ------------------------------------------------------------------
    @property
    def reading_time(self):
        """Rough reading time in minutes, derived from the body word count."""
        word_count = len(strip_tags(self.content).split())
        return max(1, round(word_count / 200))

    @property
    def toc_items(self):
        """Section headings pulled straight out of `content`, in order."""
        return [strip_tags(h).strip() for h in SECTION_HEADING.findall(self.content or "")]

    @property
    def hero_caption(self):
        """Caption text for the hero image, pulled from the content token."""
        match = HERO_IMAGE_TOKEN.search(self.content or "")
        return match.group(1).strip() if match else ""

    @property
    def content_html(self):
        """Full article body, with the hero-image token removed."""
        return HERO_IMAGE_TOKEN.sub("", self.content or "").strip()
