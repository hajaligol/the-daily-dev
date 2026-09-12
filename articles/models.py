import re

import nh3
from django.db import models
from django.utils.functional import cached_property
from django.utils.html import strip_tags
from django.utils.text import slugify
from taggit.managers import TaggableManager

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

# `Article.content` is authored exclusively through the Django admin by
# trusted staff, but it is still rendered with `|safe` on the public detail
# page, so it is sanitized as defense-in-depth rather than trusted blindly —
# a compromised or careless admin account should not be able to turn the
# content field into a stored-XSS vector. The allow-list below is exactly
# the vocabulary the editorial HTML actually uses (see the article-body
# copy seeded in migrations 0004/0005 and articles/admin.py's help text),
# so legitimate article markup renders unchanged while `<script>`, event
# handler attributes, `javascript:` URLs, etc. are stripped.
ALLOWED_TAGS = {
    "p", "h2", "h3", "blockquote", "ul", "ol", "li",
    "strong", "em", "code", "span", "a", "br", "sub", "sup",
}
ALLOWED_ATTRIBUTES = {
    "p": {"class"},
    "h2": {"class"},
    "h3": {"class"},
    "blockquote": {"class"},
    "span": {"class"},
    # "rel" is deliberately not listed here: nh3 manages that attribute
    # itself on <a> tags via `link_rel` below, and (depending on nh3
    # version) raises if it's also present in the explicit allow-list.
    "a": {"href", "title"},
}


def sanitize_article_html(raw_html):
    """Clean admin-authored article HTML down to the allow-listed vocabulary."""
    return nh3.clean(
        raw_html or "",
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        link_rel="noopener noreferrer",
    )


class Category(models.Model):
    """A newsroom section (e.g. 'Developer Journal') that articles belong to."""

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Section label shown above an article's title, e.g. 'Developer Journal'.",
    )
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Article(models.Model):
    """A single newspaper-style article shown on the 'From Our Desk' page."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="articles",
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
    topics = TaggableManager(
        blank=True,
        verbose_name="Topics",
        help_text=(
            "Optional topic tags shown in the side column, e.g. "
            "'Mindset, Debugging, Logs, Growth'."
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
    def topics_display(self):
        """Topic tags joined for display, e.g. 'Mindset, Debugging, Logs'."""
        return ", ".join(tag.name for tag in self.topics.all())

    @property
    def hero_caption(self):
        """Caption text for the hero image, pulled from the content token."""
        match = HERO_IMAGE_TOKEN.search(self.content or "")
        return match.group(1).strip() if match else ""

    @cached_property
    def content_html(self):
        """Sanitized article body, safe to render with `|safe`.

        The hero-image token is stripped first (it is plain-text markup
        specific to this project, not HTML), then the remaining body is
        passed through an allow-list HTML sanitizer before being cached on
        the instance — sanitizing is pure and can't change per-request.
        """
        without_token = HERO_IMAGE_TOKEN.sub("", self.content or "").strip()
        return sanitize_article_html(without_token)
