from django.test import TestCase
from django.urls import reverse

from .models import Article, sanitize_article_html


def make_article(**overrides):
    defaults = dict(
        title="Test Article",
        category="Testing",
        excerpt="A short teaser.",
        content="<p>Hello world.</p>",
        image="articles/wizard-hat.webp",
        image_alt="A test illustration",
        page_reference=1,
        order=0,
        is_published=True,
    )
    defaults.update(overrides)
    return Article.objects.create(**defaults)


class ArticleModelTests(TestCase):
    def test_slug_is_auto_generated_from_title(self):
        article = make_article(title="A Brand New Story", slug="")
        self.assertEqual(article.slug, "a-brand-new-story")

    def test_explicit_slug_is_preserved(self):
        article = make_article(title="Another Story", slug="custom-slug")
        self.assertEqual(article.slug, "custom-slug")

    def test_reading_time_is_at_least_one_minute(self):
        article = make_article(content="<p>Short.</p>")
        self.assertEqual(article.reading_time, 1)

    def test_reading_time_scales_with_word_count(self):
        long_body = "<p>" + ("word " * 500) + "</p>"
        article = make_article(content=long_body)
        self.assertEqual(article.reading_time, round(500 / 200))

    def test_hero_caption_extracted_from_token(self):
        article = make_article(
            content="<p>Intro.</p>[[HERO_IMAGE:A caption here.]]<p>More.</p>"
        )
        self.assertEqual(article.hero_caption, "A caption here.")

    def test_hero_caption_empty_when_token_missing(self):
        article = make_article(content="<p>No token in here.</p>")
        self.assertEqual(article.hero_caption, "")

    def test_content_html_strips_hero_image_token(self):
        article = make_article(
            content="<p>Intro.</p>[[HERO_IMAGE:caption]]<p>More.</p>"
        )
        self.assertNotIn("HERO_IMAGE", article.content_html)
        self.assertIn("Intro.", article.content_html)
        self.assertIn("More.", article.content_html)

    def test_toc_items_extracted_in_order(self):
        article = make_article(
            content=(
                "<h2>First Section</h2><p>...</p>"
                "<h2 class=\"article-section-title\">Second Section</h2>"
            )
        )
        self.assertEqual(article.toc_items, ["First Section", "Second Section"])

    def test_content_html_preserves_allowed_editorial_markup(self):
        article = make_article(
            content=(
                '<p class="has-dropcap"><span class="article-dropcap">H</span>ello.</p>'
                '<h2 class="article-section-title">A Heading</h2>'
                '<blockquote class="article-pullquote">A quote.</blockquote>'
                "<ul><li>One</li><li>Two</li></ul>"
                "<p>Some <code>inline code</code> and <strong>bold</strong> text.</p>"
            )
        )
        html = article.content_html
        self.assertIn('<span class="article-dropcap">H</span>', html)
        self.assertIn('<h2 class="article-section-title">A Heading</h2>', html)
        self.assertIn('<blockquote class="article-pullquote">A quote.</blockquote>', html)
        self.assertIn("<li>One</li>", html)
        self.assertIn("<code>inline code</code>", html)
        self.assertIn("<strong>bold</strong>", html)


class ArticleContentSanitizationTests(TestCase):
    """Guards the XSS-prevention behaviour of `content_html` directly."""

    def test_script_tags_are_stripped(self):
        html = sanitize_article_html("<p>Hi</p><script>alert('xss')</script>")
        self.assertNotIn("<script", html)
        self.assertNotIn("alert(", html)

    def test_inline_event_handlers_are_stripped(self):
        html = sanitize_article_html('<p onclick="evil()">Click me</p>')
        self.assertNotIn("onclick", html)

    def test_javascript_urls_are_stripped(self):
        html = sanitize_article_html('<a href="javascript:evil()">link</a>')
        self.assertNotIn("javascript:", html)

    def test_disallowed_tags_are_removed_but_text_kept(self):
        html = sanitize_article_html("<iframe src='https://evil.example'></iframe><p>Safe</p>")
        self.assertNotIn("<iframe", html)
        self.assertIn("Safe", html)


class ArticleQuerysetTests(TestCase):
    def setUp(self):
        # Distinct, high `order` values so these fixtures can never collide
        # with the six seeded launch articles (order 1-6) also present in
        # the test database via migrations.
        self.published = [
            make_article(title=f"Published {i}", order=1000 + i, is_published=True)
            for i in range(4)
        ]
        self.unpublished = make_article(
            title="Unpublished", order=1099, is_published=False
        )

    def test_list_view_shows_only_published_articles(self):
        response = self.client.get(reverse("articles:list"))
        self.assertEqual(response.status_code, 200)
        titles = [a.title for a in response.context["articles"]]
        self.assertIn("Published 0", titles)
        self.assertNotIn("Unpublished", titles)

    def test_detail_view_returns_200_for_published_article(self):
        article = self.published[0]
        response = self.client.get(
            reverse("articles:detail", args=[article.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, article.title)

    def test_detail_view_404s_for_unpublished_article(self):
        response = self.client.get(
            reverse("articles:detail", args=[self.unpublished.slug])
        )
        self.assertEqual(response.status_code, 404)

    def test_detail_view_404s_for_unknown_slug(self):
        response = self.client.get(
            reverse("articles:detail", args=["does-not-exist"])
        )
        self.assertEqual(response.status_code, 404)

    def test_previous_and_next_articles_follow_order(self):
        middle = self.published[1]
        response = self.client.get(
            reverse("articles:detail", args=[middle.slug])
        )
        self.assertEqual(
            response.context["previous_article"], self.published[0]
        )
        self.assertEqual(response.context["next_article"], self.published[2])

    def test_related_articles_exclude_self_and_are_limited_to_three(self):
        response = self.client.get(
            reverse("articles:detail", args=[self.published[0].slug])
        )
        related = list(response.context["related_articles"])
        self.assertNotIn(self.published[0], related)
        self.assertLessEqual(len(related), 3)


class SeededImagePathMigrationTests(TestCase):
    """Regression test for the historical broken-image-path bug.

    A fresh database built purely from migrations must not carry the stale
    SVG paths originally seeded in 0002_seed_articles (see
    0006_fix_seeded_image_paths for the full story).
    """

    def test_no_seeded_article_points_at_the_old_broken_svg_paths(self):
        broken_suffixes = (
            "debugging-engraving.svg",
            "architecture-engraving.svg",
            "toolbox-engraving.svg",
            "growth-engraving.svg",
            "balance-engraving.svg",
        )
        for article in Article.objects.all():
            for suffix in broken_suffixes:
                self.assertFalse(
                    str(article.image).endswith(suffix),
                    f"{article.title!r} still points at the broken seed image {suffix!r}",
                )
