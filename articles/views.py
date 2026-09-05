from django.views.generic import ListView

from .models import Article


class ArticleListView(ListView):
    """Renders the 'From Our Desk' article listing page — published articles
    presented as a two-column newspaper features page."""

    model = Article
    template_name = "articles/article_list.html"
    context_object_name = "articles"

    def get_queryset(self):
        return Article.objects.filter(is_published=True)
