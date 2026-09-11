from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Article


class ArticleSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Article.objects.filter(is_published=True)

    def lastmod(self, article):
        return article.updated_at

    def location(self, article):
        return reverse("articles:detail", args=[article.slug])


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return ["newsroom:index", "newsroom:contact", "articles:list"]

    def location(self, item):
        return reverse(item)
