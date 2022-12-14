from enum import Enum
from typing import Optional

from django.forms import CharField, ChoiceField, Form, JSONField, ModelForm
from django.forms.widgets import CheckboxSelectMultiple, Select, TextInput

from form.canvas import get_current_term, get_next_term, get_user_canvas_sites
from form.terms import CURRENT_TERM, NEXT_TERM

from .models import AutoAdd, Request, SectionEnrollment, Subject


class RequestForm(ModelForm):
    additional_enrollments = JSONField()

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
            "included_sections",
        )
        labels = {
            "proxy_requester": "Request on behalf of",
            "included_sections": "Include sections",
        }
        widgets = {
            "copy_from_course": Select,
            "additional_enrollments": TextInput,
            "included_sections": CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        course_sections = kwargs["initial"]["course_sections"]
        if course_sections:
            course_sections = [
                (section, section.get_canvas_course_code) for section in course_sections
            ]
            self.fields["included_sections"].choices = course_sections
        else:
            del self.fields["included_sections"]
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

    @classmethod
    def get_instructor_canvas_sites(cls, username: str) -> Optional[list[tuple]]:
        canvas_sites = get_user_canvas_sites(username)
        if not canvas_sites:
            return None
        return [(site.id, f"{site.name} ({site.id})") for site in canvas_sites]

    def get_copy_from_course_choices(self, username: str):
        copy_from_course_choices: list = [("", "---------")]
        canvas_sites = self.get_instructor_canvas_sites(username)
        if canvas_sites:
            copy_from_course_choices += canvas_sites
        self.fields["copy_from_course"].disabled = not canvas_sites
        self.fields["copy_from_course"].widget.choices = copy_from_course_choices


class SectionEnrollmentForm(ModelForm):
    class CanvasRoleDisplay(Enum):
        TA = "TA"
        INSTRUCTOR = "Instructor"
        DESIGNER = "Designer"
        LIBRARIAN = "Librarian"

        @classmethod
        @property
        def choices(cls):
            return [(member.name, member.value) for member in cls]

    class Meta:
        model = SectionEnrollment
        fields = ("user", "role")
        widgets = {"user": TextInput}
        labels = {"user": "Pennkey"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"].widget.choices = self.CanvasRoleDisplay.choices


class AutoAddForm(ModelForm):
    class Meta:
        model = AutoAdd
        fields = "__all__"
        widgets = {"user": TextInput}
        labels = {"user": "Pennkey"}


class SyncSectionForm(Form):
    subject = ChoiceField()
    course_number = CharField()
    section_number = CharField()
    term = ChoiceField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        subjects = Subject.get_subjects_as_choices()
        self.fields["subject"].choices = subjects
        terms = [
            ("", "---------"),
            (CURRENT_TERM, get_current_term()),
            (NEXT_TERM, get_next_term()),
        ]
        self.fields["term"].choices = terms
