from django.views.generic import DetailView, ListView

from .models import Article


class ArticleListView(ListView):
    """Renders the 'From Our Desk' article listing page — published articles
    presented as a two-column newspaper features page."""

    model = Article
    template_name = "articles/article_list.html"
    context_object_name = "articles"

    def get_queryset(self):
        return Article.objects.filter(is_published=True).select_related("category")


class ArticleDetailView(DetailView):
    """Renders a single Article as a dedicated newspaper feature page."""

    model = Article
    template_name = "articles/article_detail.html"
    context_object_name = "article"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return (
            Article.objects.filter(is_published=True)
            .select_related("category")
            .prefetch_related("topics")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object
        published = Article.objects.filter(is_published=True)

        context["previous_article"] = (
            published.filter(order__lt=article.order).order_by("-order").first()
        )
        context["next_article"] = (
            published.filter(order__gt=article.order).order_by("order").first()
        )
        context["related_articles"] = (
            published.exclude(pk=article.pk).order_by("order")[:3]
        )
        return context
