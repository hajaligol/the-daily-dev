from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from articles.models import Article

from .forms import ContactForm


class IndexView(TemplateView):
    """Renders the front page of The Daily Dev."""

    template_name = "newsroom/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["latest_articles"] = (
            Article.objects.filter(is_published=True).order_by("-created_at")[:3]
        )
        return context


class ContactView(FormView):
    """Renders the Contact page and handles the 'Send Us a Message' form.

    There is no outbound email/notification integration configured for this
    project yet, so a successful submission is saved as a `ContactMessage`
    (visible in the Django admin) rather than claiming to have been emailed
    anywhere. Swap `form_valid` for a real notification once one exists.
    """

    template_name = "newsroom/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("newsroom:contact")

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            "Your message has been received at the newsroom desk. "
            "We read every message and will write back soon.",
        )
        return super().form_valid(form)
