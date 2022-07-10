from datetime import datetime
from functools import reduce
from typing import Callable, Optional, Union, cast

from canvasapi.course import Course
from config.config import PROD_URL
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, QuerySet
from django.forms.utils import ErrorList
from django.http import HttpResponse
from django.urls.base import reverse
from django.views.generic import DetailView, FormView, ListView, TemplateView

from form.templatetags.canvas_site_filters import get_term
from form.terms import CURRENT_TERM, NEXT_TERM
from form.utils import get_sort_value

from .forms import RequestForm, SectionEnrollmentForm
from .models import Enrollment, Request, School, Section, SectionEnrollment, User

HOME_LIST_LIMIT = 5
HOME_LIST_INCREMENT = 5


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = "form/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = cast(User, self.request.user)
        sections = user.get_sections()
        sections_count = sections.count()
        context["sections"] = sections[:HOME_LIST_LIMIT]
        requests = user.get_requests()
        requests_count = requests.count()
        context["requests"] = requests[:HOME_LIST_LIMIT]
        canvas_sites = user.get_canvas_sites()
        canvas_sites_count = len(canvas_sites)
        if canvas_sites:
            canvas_sites = canvas_sites[:HOME_LIST_LIMIT]
        context["canvas_sites"] = canvas_sites
        context["canvas_url"] = f"{PROD_URL}/courses"
        context["current_term"] = CURRENT_TERM
        context["next_term"] = NEXT_TERM
        context["sort_requests_created_at"] = "created_at"
        context["sort_requests_section"] = "section__section_code"
        context["sort_requests_requester"] = "requester"
        context["sort_requests_status"] = "-status"
        context["limit_requests"] = HOME_LIST_LIMIT
        context["load_more_requests"] = requests_count > HOME_LIST_LIMIT
        context["sort_sections_section"] = "-section_code"
        context["sort_sections_title"] = "title"
        context["sort_sections_schedule_type"] = "schedule_type"
        context["sort_sections_instructors"] = "instructors"
        context["sort_sections_requester"] = "request__requester"
        context["sort_sections_created_at"] = "request__created_at"
        context["limit_sections"] = HOME_LIST_LIMIT
        context["load_more_sections"] = sections_count > HOME_LIST_LIMIT
        context["sort_canvas_sites_course_id"] = "course_id"
        context["sort_canvas_sites_name"] = "name"
        context["sort_canvas_sites_term"] = "term"
        context["sort_canvas_sites_canvas_course_id"] = "canvas_course_id"
        context["limit_canvas_sites"] = HOME_LIST_LIMIT
        context["load_more_canvas_sites"] = canvas_sites_count > HOME_LIST_LIMIT
        return context


class MyRequestsView(TemplateView):
    template_name = "form/my_requests.html"

    @staticmethod
    def sort_by_section_code(request: Request) -> str:
        return request.section.section_code

    def sort_by_other_requester(self, request: Request) -> str:
        user = cast(User, self.request.user)
        return request.get_other_requester(user)

    @staticmethod
    def sort_by_date_requested(request: Request) -> datetime:
        return request.created_at

    @staticmethod
    def sort_by_status(request: Request) -> str:
        return request.status

    @classmethod
    def get_sort_function(cls, sort) -> Callable:
        sort = sort.replace("-", "")
        sort_functions = {
            "section_code": cls.sort_by_section_code,
            "requested_by": cls.sort_by_other_requester,
            "date_requested": cls.sort_by_date_requested,
            "status": cls.sort_by_status,
        }
        return sort_functions.get(sort, cls.sort_by_date_requested)

    @classmethod
    def sort_requests(
        cls, requests: Union[QuerySet[Request], list[Request]], sort: str
    ) -> list[Request]:
        requests = list(requests)
        reverse = "-" in sort
        function = cls.get_sort_function(sort)
        requests.sort(key=function, reverse=reverse)
        return requests

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = cast(User, self.request.user)
        requests = user.get_requests()
        requests_count = requests.count()
        limit = int(self.request.GET.get("limit", HOME_LIST_LIMIT))
        sort = self.request.GET.get("sort", "")
        if sort:
            requests = requests[:limit]
            requests = self.sort_requests(requests, sort)
        else:
            limit = limit + HOME_LIST_INCREMENT
            requests = requests[:limit]
        context["requests"] = requests
        context["sort_requests_section"] = get_sort_value("section__section_code", sort)
        context["sort_requests_created_at"] = get_sort_value("created_at", sort, False)
        context["sort_requests_requester"] = get_sort_value("requester", sort)
        context["sort_requests_status"] = get_sort_value("status", sort)
        context["limit_requests"] = limit
        context["load_more_requests"] = requests_count > limit
        return context


class MyCoursesView(TemplateView):
    template_name = "form/section_list_table.html"

    @staticmethod
    def sort_by_section_code(section: Section) -> str:
        return section.section_code

    @staticmethod
    def sort_by_title(section: Section) -> str:
        return section.title

    @staticmethod
    def sort_by_schedule_type(section: Section) -> str:
        return section.schedule_type.sched_type_code

    def sort_by_other_requester(self, section: Section) -> str:
        user = cast(User, self.request.user)
        return section.get_other_requester(user)

    @staticmethod
    def sort_by_date_requested(section: Section) -> Optional[datetime]:
        request = section.get_request()
        if not request:
            return None
        return request.created_at

    @classmethod
    def get_sort_function(cls, sort) -> Callable:
        sort = sort.replace("-", "")
        sort_functions = {
            "section_code": cls.sort_by_section_code,
            "title": cls.sort_by_title,
            "schedule_type": cls.sort_by_schedule_type,
            "requested_by": cls.sort_by_other_requester,
            "date_requested": cls.sort_by_date_requested,
        }
        return sort_functions.get(sort, cls.sort_by_date_requested)

    @classmethod
    def sort_sections(
        cls, sections: Union[QuerySet[Section], list[Section]], sort: str
    ) -> list[Section]:
        sections = list(sections)
        reverse = "-" in sort
        function = cls.get_sort_function(sort)
        sections.sort(key=function, reverse=reverse)
        return sections

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = cast(User, self.request.user)
        sections = user.get_sections()
        sections_count = sections.count()
        limit = int(self.request.GET.get("limit", HOME_LIST_LIMIT))
        sort = self.request.GET.get("sort", "")
        if sort:
            sections = sections[:limit]
            sections = self.sort_sections(sections, sort)
        else:
            limit = limit + HOME_LIST_INCREMENT
            sections = sections[:limit]
        context["sections"] = sections[:limit]
        context["sort_sections_section"] = get_sort_value("section_code", sort)
        context["sort_sections_title"] = get_sort_value("title", sort)
        context["sort_sections_schedule_type"] = get_sort_value("schedule_type", sort)
        context["sort_sections_instructors"] = get_sort_value("instructors", sort)
        context["sort_sections_requester"] = get_sort_value("request__requester", sort)
        context["sort_sections_created_at"] = get_sort_value(
            "request__created_at", sort
        )
        context["limit_sections"] = limit
        context["load_more_sections"] = sections_count > limit
        return context


class MyCanvasSitesView(TemplateView):
    template_name = "form/my_canvas_sites.html"

    @staticmethod
    def sort_by_course_id(course: Course) -> str:
        return course.sis_course_id or ""

    @staticmethod
    def sort_by_name(course: Course) -> str:
        return course.name or ""

    @staticmethod
    def sort_by_term(course: Course) -> str:
        return get_term(course.enrollment_term_id)

    @staticmethod
    def sort_by_canvas_course_id(course: Course) -> int:
        return course.id

    @classmethod
    def get_sort_function(cls, sort) -> Callable:
        sort = sort.replace("-", "")
        sort_functions = {
            "course_id": cls.sort_by_course_id,
            "name": cls.sort_by_name,
            "term": cls.sort_by_term,
            "canvas_course_id": cls.sort_by_canvas_course_id,
        }
        return sort_functions.get(sort, cls.sort_by_course_id)

    @classmethod
    def sort_canvas_sites(cls, canvas_sites: list[Course], sort: str):
        reverse = "-" in sort
        function = cls.get_sort_function(sort)
        canvas_sites.sort(key=function, reverse=reverse)
        return canvas_sites

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = cast(User, self.request.user)
        canvas_sites = user.get_canvas_sites()
        canvas_sites_count = len(canvas_sites)
        limit = int(self.request.GET.get("limit", HOME_LIST_LIMIT))
        sort = self.request.GET.get("sort", "")
        if sort:
            canvas_sites = self.sort_canvas_sites(canvas_sites, sort)
        else:
            limit = limit + HOME_LIST_INCREMENT
        context["canvas_sites"] = canvas_sites[:limit] if canvas_sites else []
        context["sort_canvas_sites_course_id"] = get_sort_value("course_id", sort)
        context["sort_canvas_sites_name"] = get_sort_value("name", sort)
        context["sort_canvas_sites_term"] = get_sort_value("term", sort)
        context["sort_canvas_sites_canvas_course_id"] = get_sort_value(
            "canvas_course_id", sort
        )
        context["limit_canvas_sites"] = limit
        context["load_more_canvas_sites"] = canvas_sites_count > limit
        return context


class SectionListView(ListView):
    model = Section
    paginate_by = 30
    context_object_name = "sections"

    @staticmethod
    def get_request_isnull(status):
        request_isnull_statues = {"requested": False, "unrequested": True}
        return request_isnull_statues.get(status)

    def get_queryset(self):
        request = self.request.GET
        sections = Section.objects.filter(primary_section__isnull=True)
        clear = request.get("clear")
        if clear:
            return sections
        term = request.get("term")
        status = request.get("status")
        sort = request.get("sort")
        search = request.get("search")
        if term == str(CURRENT_TERM):
            sections = sections.filter(term=CURRENT_TERM)
        elif term == str(NEXT_TERM):
            sections = sections.filter(term=NEXT_TERM)
        if status:
            request_isnull = self.get_request_isnull(status)
            sections = sections.filter(request__isnull=request_isnull)
        if sort == "date":
            sections = sections.order_by("-created_at")
        if search:
            search_terms = search.split()
            sections = sections.filter(
                reduce(
                    lambda query_one, query_two: query_one & query_two,
                    [
                        Q(section_code__icontains=search_term)
                        | Q(also_offered_as__section_code__icontains=search_term)
                        | Q(title__icontains=search_term)
                        | Q(schedule_type__sched_type_code__icontains=search_term)
                        | Q(instructors__username__icontains=search_term)
                        | Q(instructors__first_name__icontains=search_term)
                        | Q(instructors__last_name__icontains=search_term)
                        for search_term in search_terms
                    ],
                )
            )
        return sections.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clear = self.request.GET.get("clear")
        if clear:
            term = status = search = ""
        else:
            term = self.request.GET.get("term")
            status = self.request.GET.get("status")
            search = self.request.GET.get("search") or ""
        context["current_term"] = str(CURRENT_TERM)
        context["next_term"] = str(NEXT_TERM)
        context["term"] = term
        context["status"] = status
        context["search"] = search
        return context


class RequestDetailView(DetailView):
    model = Request


class RequestFormView(FormView):
    form_class = RequestForm
    template_name = "form/section_request.html"

    def get_section(self):
        section_code = self.kwargs["pk"]
        return Section.objects.get(section_code=section_code)

    def get_initial(self):
        initial = super().get_initial()
        username = cast(User, self.request.user).username
        user = User.objects.get(username=username)
        section = self.get_section()
        course_sections = section.course_sections.all()
        instructors = section.instructors.all()
        initial_values = {"course_sections": course_sections}
        if instructors and user not in instructors:
            initial_values["instructors"] = instructors
            if instructors.count() == 1:
                initial_values["proxy_requester"] = instructors.first()
        else:
            initial_values["proxy_requester"] = user
        initial.update(**initial_values)
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        section = self.get_section()
        is_sas_section = section.school.school_code == School.SAS_SCHOOL_CODE
        user_is_instructor = "instructors" not in self.get_initial()
        course_sections = section.course_sections.all()
        context["section"] = section
        context["user_is_instructor"] = user_is_instructor
        context["is_sas_section"] = is_sas_section
        context["section_enrollment_form"] = SectionEnrollmentForm()
        context["course_sections"] = course_sections
        return context

    def form_valid(self, form):
        values = cast(dict, form.cleaned_data)
        values["requester"] = self.request.user
        values["copy_from_course"] = values["copy_from_course"] or None
        section_code = self.kwargs["pk"]
        section = Section.objects.get(section_code=section_code)
        additional_enrollments = values.pop("additional_enrollments")
        included_sections = None
        if "included_sections" in values:
            included_sections = values.pop("included_sections")
        request = Request.objects.create(section=section, **values)
        additional_enrollments = [
            enrollment for enrollment in additional_enrollments if enrollment
        ]
        for index, enrollment in enumerate(additional_enrollments):
            user = User.get_user(enrollment["user"])
            role = SectionEnrollment.CanvasRole.get_value(enrollment["role"])
            additional_enrollments[index] = SectionEnrollment.objects.create(
                user=user, role=role, request=request
            )
        request.additional_enrollments.set(additional_enrollments)
        if included_sections:
            request.included_sections.set(included_sections)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("sections")


class CopyFromCourseView(TemplateView):
    template_name = "form/copy_from_course.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.GET.get("proxy_requester")
        try:
            username = User.objects.get(id=user_id).username
        except Exception:
            username = None
        canvas_sites = list()
        if username:
            canvas_sites = RequestForm.get_instructor_canvas_sites(username=username)
        context["canvas_sites"] = canvas_sites
        return context


class ExcludeAnnouncementsView(TemplateView):
    template_name = "form/exclude_announcements.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        copy_from_course = self.request.GET["copy_from_course"]
        context["copy_from_course"] = bool(copy_from_course)
        return context


class SectionEnrollmentView(TemplateView):
    template_name = "form/section_enrollment.html"

    @staticmethod
    def get_pennkey(user_display: str) -> str:
        pennkey_start = user_display.find("(") + 1
        pennkey_end = user_display.find(")")
        return user_display[pennkey_start:pennkey_end]

    @staticmethod
    def get_role(role: str) -> str:
        return Enrollment.CanvasRole[role.upper()].name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        values = self.request.GET
        new_enrollment_count = values["enrollmentCount"]
        editing = "pennkey" in values and "role" in values
        if editing:
            pennkey = self.get_pennkey(values["pennkey"])
            role = self.get_role(values["role"])
            form_data = {
                "user": pennkey,
                "role": role,
            }
            form = SectionEnrollmentForm(form_data)
            form.auto_id = f"id_%s_{new_enrollment_count}"
        else:
            new_enrollment_count = int(new_enrollment_count) + 1
            form = SectionEnrollmentForm(auto_id=f"id_%s_{new_enrollment_count}")
        div_id = f"id_enrollment_user_{new_enrollment_count}"
        button_id = f"id_load_user_{new_enrollment_count}"
        remove_button_id = f"id_remove_{new_enrollment_count}"
        context["div_id"] = div_id
        context["button_id"] = button_id
        context["remove_button_id"] = remove_button_id
        context["form"] = form
        return context


class EnrollmentUserView(TemplateView):
    template_name = "form/enrollment_user.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        values = self.request.GET
        enrollment_count = values["enrollmentCount"]
        context["enrollment_count"] = enrollment_count
        div_id = f"id_enrollment_user_{enrollment_count}"
        context["div_id"] = div_id
        pennkey = values["pennkey"]
        user = User.get_user(pennkey)
        if not user:
            button_id = f"id_load_user_{enrollment_count}"
            context["button_id"] = button_id
            form_data = {"user": pennkey}
            form = SectionEnrollmentForm(form_data)
            form.auto_id = f"id_%s_{enrollment_count}"
            form.cleaned_data = dict()
            error_text = (
                f'User with pennkey "{pennkey}" not found. Please try a different'
                " pennkey or leave a note below if you believe this one is correct."
            )
            form.errors["user"] = ErrorList([error_text])
            context["form"] = form
            context["error"] = True
            return context
        base = "additional_enrollment"
        base_id = f"id_{base}"
        pennkey_name = f"{base}_pennkey_{enrollment_count}"
        pennkey_id = f"{base_id}_pennkey_{enrollment_count}"
        role_name = f"{base}_role_{enrollment_count}"
        role_id = f"{base_id}_role_{enrollment_count}"
        edit_button_id = f"id_edit_{enrollment_count}"
        remove_button_id = f"id_remove_{enrollment_count}"
        context["enrollment_count"] = enrollment_count
        context["pennkey_name"] = pennkey_name
        context["pennkey_id"] = pennkey_id
        context["role_name"] = role_name
        context["role_id"] = role_id
        context["edit_button_id"] = edit_button_id
        context["remove_button_id"] = remove_button_id
        context["enrollment_user"] = user
        context["role"] = values["role"].title()
        return context


def delete_enrollment_user(request):
    return HttpResponse()
