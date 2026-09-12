from django.views.generic import DetailView, ListView

from .models import Article


class ArticleListView(ListView):
    """Renders the 'From Our Desk' article listing page — published articles
    presented as a two-column newspaper features page, six to a page."""

    model = Article
    template_name = "articles/article_list.html"
    context_object_name = "articles"
    paginate_by = 6

    def get_queryset(self):
        return Article.objects.filter(is_published=True).select_related("category")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # A trailing page can hold fewer than `paginate_by` articles (e.g.
        # only 1 on the last page). Without help the two-column grid then
        # runs shorter than a full page, so the page visibly changes
        # length as you paginate. `placeholder_range` fills out the
        # remaining grid slots with invisible placeholders that reserve
        # the same space a real article would take up, keeping every
        # page the same length regardless of how many articles it holds.
        articles_on_page = len(context.get(self.context_object_name) or [])
        context["placeholder_range"] = range(max(0, self.paginate_by - articles_on_page))
        return context


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

        # Articles are listed newest-first, so "previous" (appears earlier
        # on the list) is the next-more-recent article, and "next" (appears
        # later on the list) is the next-older one.
        context["previous_article"] = (
            published.filter(created_at__gt=article.created_at)
            .order_by("created_at")
            .first()
        )
        context["next_article"] = (
            published.filter(created_at__lt=article.created_at)
            .order_by("-created_at")
            .first()
        )
        context["related_articles"] = (
            published.exclude(pk=article.pk).order_by("-created_at")[:3]
        )
        return context
