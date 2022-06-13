from typing import Optional
from canvasapi.course import Course
from django.core.exceptions import ValidationError
from django.forms import EmailField, Form, ModelForm
from django.forms.widgets import Select

from form.canvas import get_user_canvas_sites

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
        widgets = {"copy_from_course": Select}

    @staticmethod
    def get_canvas_site_id(canvas_site: Course) -> int:
        return canvas_site.id

    @classmethod
    def get_instructor_canvas_sites(cls, username: str) -> Optional[list[tuple]]:
        canvas_sites = get_user_canvas_sites(username)
        if not canvas_sites:
            return None
        canvas_sites.sort(key=cls.get_canvas_site_id, reverse=True)
        return [(site.id, f"{site.name} ({site.id})") for site in canvas_sites]

    def get_copy_from_course_choices(self, username: str):
        copy_from_course_choices = [("", "---------")]
        canvas_sites = self.get_instructor_canvas_sites(username)
        if canvas_sites:
            copy_from_course_choices += canvas_sites
        self.fields["copy_from_course"].disabled = not canvas_sites
        self.fields["copy_from_course"].widget.choices = copy_from_course_choices
        print(self.fields["copy_from_course"].widget.choices)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "instructors" not in kwargs["initial"]:
            username = self.initial["proxy_requester"].username
            self.get_copy_from_course_choices(username)
            del self.fields["proxy_requester"]
            return
        instructors = kwargs["initial"]["instructors"]
        self.fields["proxy_requester"].queryset = instructors
        single_instructor = "proxy_requester" in kwargs["initial"]
        if single_instructor:
            username = instructors.first().username
            self.get_copy_from_course_choices(username)
            self.fields["proxy_requester"].disabled = True


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
