from django.forms import ModelForm

from .models import Request


class RequestForm(ModelForm):
    class Meta:
        model = Request
        fields = (
            "title_override",
            "copy_from_course",
            "reserves",
            "lps_online",
            "exclude_announcements",
            "additional_enrollments",
            "additional_instructions",
        )
