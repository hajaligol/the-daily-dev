from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from articles.models import Article

from .models import ContactMessage


class IndexViewTests(TestCase):
    def setUp(self):
        for i in range(5):
            Article.objects.create(
                title=f"Article {i}",
                category="Testing",
                excerpt="Excerpt",
                image="articles/wizard-hat.webp",
                image_alt="Alt text",
                order=1000 + i,
                is_published=True,
            )

    def test_index_returns_200(self):
        response = self.client.get(reverse("newsroom:index"))
        self.assertEqual(response.status_code, 200)

    def test_index_shows_at_most_three_latest_articles(self):
        response = self.client.get(reverse("newsroom:index"))
        self.assertLessEqual(len(response.context["latest_articles"]), 3)

    def test_index_excludes_unpublished_articles(self):
        Article.objects.create(
            title="Hidden Draft",
            category="Testing",
            excerpt="Excerpt",
            image="articles/wizard-hat.webp",
            image_alt="Alt text",
            order=2000,
            is_published=False,
        )
        response = self.client.get(reverse("newsroom:index"))
        titles = [a.title for a in response.context["latest_articles"]]
        self.assertNotIn("Hidden Draft", titles)


VALID_CONTACT_DATA = {
    "name": "Ada Lovelace",
    "email": "ada@example.com",
    "subject": "Hello from the desk",
    "message": "Just saying hi to the newsroom.",
}


class ContactViewTests(TestCase):
    def test_contact_page_returns_200(self):
        response = self.client.get(reverse("newsroom:contact"))
        self.assertEqual(response.status_code, 200)

    def test_valid_submission_creates_message_and_redirects(self):
        response = self.client.post(
            reverse("newsroom:contact"), data=VALID_CONTACT_DATA
        )
        self.assertRedirects(response, reverse("newsroom:contact"))
        self.assertEqual(ContactMessage.objects.count(), 1)
        saved = ContactMessage.objects.get()
        self.assertEqual(saved.email, "ada@example.com")

    def test_valid_submission_shows_success_message(self):
        response = self.client.post(
            reverse("newsroom:contact"), data=VALID_CONTACT_DATA, follow=True
        )
        messages = [str(m) for m in response.context["messages"]]
        self.assertTrue(any("newsroom desk" in m for m in messages))

    def test_missing_required_fields_does_not_save_and_shows_errors(self):
        response = self.client.post(reverse("newsroom:contact"), data={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertTrue(response.context["form"].errors)

    def test_invalid_email_is_rejected(self):
        data = {**VALID_CONTACT_DATA, "email": "not-an-email"}
        response = self.client.post(reverse("newsroom:contact"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertIn("email", response.context["form"].errors)

    def test_whitespace_is_trimmed_from_text_fields(self):
        data = {**VALID_CONTACT_DATA, "name": "  Ada Lovelace  "}
        self.client.post(reverse("newsroom:contact"), data=data)
        saved = ContactMessage.objects.get()
        self.assertEqual(saved.name, "Ada Lovelace")

    def test_submission_without_csrf_token_is_rejected(self):
        strict_client = Client(enforce_csrf_checks=True)
        response = strict_client.post(
            reverse("newsroom:contact"), data=VALID_CONTACT_DATA
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(ContactMessage.objects.count(), 0)

    @override_settings(CONTACT_NOTIFICATION_EMAIL="")
    def test_no_email_sent_when_notification_address_not_configured(self):
        self.client.post(reverse("newsroom:contact"), data=VALID_CONTACT_DATA)
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(CONTACT_NOTIFICATION_EMAIL="editor@example.com")
    def test_email_sent_when_notification_address_configured(self):
        self.client.post(reverse("newsroom:contact"), data=VALID_CONTACT_DATA)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["editor@example.com"])

    def test_success_message_never_claims_an_email_was_sent(self):
        # Regression guard for the "do not invent fake operational claims"
        # requirement: the visitor-facing message must not promise an email
        # reply exists unless one is actually configured/sent.
        response = self.client.post(
            reverse("newsroom:contact"), data=VALID_CONTACT_DATA, follow=True
        )
        messages_text = " ".join(str(m) for m in response.context["messages"])
        self.assertNotIn("emailed", messages_text.lower())


class RemovedRouteTests(TestCase):
    """`newsroom/blog_list.html` was dead prototype code with no route, no
    view providing its `posts` context, and `href="#"` placeholder links —
    it was removed rather than wired up. This just documents that no such
    route exists."""

    def test_no_legacy_blog_list_route(self):
        response = self.client.get("/blog/")
        self.assertEqual(response.status_code, 404)


class SeoAndOpsRouteTests(TestCase):
    def test_sitemap_returns_200(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)

    def test_robots_txt_returns_200_and_disallows_admin(self):
        response = self.client.get("/robots.txt")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Disallow: /admin/")

    def test_healthz_returns_200(self):
        response = self.client.get("/healthz/")
        self.assertEqual(response.status_code, 200)
