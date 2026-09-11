import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from articles.models import Article

from .forms import ContactForm

logger = logging.getLogger(__name__)


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

    A successful submission is always saved as a `ContactMessage` (visible
    in the Django admin). It is additionally emailed to
    `settings.CONTACT_NOTIFICATION_EMAIL` when that setting is configured —
    see `_notify_desk` below.
    """

    template_name = "newsroom/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("newsroom:contact")

    def form_valid(self, form):
        contact_message = form.save()
        self._notify_desk(contact_message)
        messages.success(
            self.request,
            "Your message has been received at the newsroom desk. "
            "We read every message and will write back soon.",
        )
        return super().form_valid(form)

    def _notify_desk(self, contact_message):
        """Best-effort email notification for a new contact submission.

        Only fires when CONTACT_NOTIFICATION_EMAIL is configured. A failure
        here (e.g. SMTP misconfigured) is logged but never surfaced to the
        visitor or allowed to break the submission — the message is already
        saved and readable in the admin regardless.
        """
        recipient = settings.CONTACT_NOTIFICATION_EMAIL
        if not recipient:
            return

        try:
            send_mail(
                subject=f"[The Daily Dev] {contact_message.subject}",
                message=(
                    f"From: {contact_message.name} <{contact_message.email}>\n\n"
                    f"{contact_message.message}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
        except Exception:
            logger.exception("Failed to send contact-form notification email.")
