from django.views.generic import TemplateView


class IndexView(TemplateView):
    """Renders the front page of The Daily Dev."""

    template_name = "newsroom/index.html"
