from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """Backs the 'Send Us a Message' form on the Contact page.

    Field-level error messages are written in the same editorial voice as
    the rest of the site rather than generic framework defaults.
    """

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "field-input",
                    "placeholder": "Your name",
                    "autocomplete": "name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "field-input",
                    "placeholder": "your@email.com",
                    "autocomplete": "email",
                }
            ),
            "subject": forms.TextInput(
                attrs={
                    "class": "field-input",
                    "placeholder": "What's this about?",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "field-input field-textarea",
                    "placeholder": "Tell us more…",
                    "rows": 7,
                }
            ),
        }
        error_messages = {
            "name": {
                "required": "Please tell us who's writing in.",
            },
            "email": {
                "required": "We'll need an address to write back to.",
                "invalid": "That doesn't look like a deliverable address — please check it.",
            },
            "subject": {
                "required": "Give your message a headline of its own.",
            },
            "message": {
                "required": "The message field is looking a little empty.",
            },
        }

    def clean_name(self):
        return self.cleaned_data["name"].strip()

    def clean_subject(self):
        return self.cleaned_data["subject"].strip()

    def clean_message(self):
        return self.cleaned_data["message"].strip()
