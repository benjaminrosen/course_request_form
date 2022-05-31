from django.core.exceptions import ValidationError
from django.forms import EmailField, Form, ModelForm

from .models import Request


class RequestForm(ModelForm):
    class Meta:
        model = Request
        fields = (
            "proxy_requester",
            "title_override",
            "copy_from_course",
            "reserves",
            "lps_online",
            "exclude_announcements",
            "additional_enrollments",
            "additional_instructions",
        )
        labels = {"proxy_requester": "Request on behalf of"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        proxy_requester = self.fields["proxy_requester"]
        if not "instructors" in kwargs["initial"]:
            del proxy_requester
            return
        instructors = kwargs["initial"]["instructors"]
        proxy_requester.queryset = instructors
        if "proxy_requester" in kwargs["initial"]:
            proxy_requester.disabled = True


class EmailForm(Form):
    new_email = EmailField()
    confirm_email = EmailField()

    def __init__(self, username, *args, **kwargs):
        self.username = username
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data:
            return
        cleaned_data["username"] = self.username
        new_email = cleaned_data.get("new_email")
        confirm_email = cleaned_data.get("confirm_email")

        if confirm_email != new_email:
            raise ValidationError(
                "Emails don't match. Please confirm your new email address."
            )
