from django.views.generic import TemplateView

from articles.models import Article


class IndexView(TemplateView):
    """Renders the front page of The Daily Dev."""

    template_name = "newsroom/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["latest_articles"] = (
            Article.objects.filter(is_published=True).order_by("-created_at")[:3]
        )
        return context
