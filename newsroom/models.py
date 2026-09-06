from django.db import models


class ContactMessage(models.Model):
    """A message submitted through the Contact page's 'Send Us a Message'
    form. Stored so it can be read from the Django admin — there is no
    outbound email/notification wiring yet, so nothing is sent anywhere;
    submitting the form simply files the letter at the newsroom desk."""

    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Contact message"
        verbose_name_plural = "Contact messages"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} — {self.name}"
