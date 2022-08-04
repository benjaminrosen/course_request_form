from functools import reduce
from typing import Callable, Optional, Union, cast

from canvasapi.course import Course
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import NON_FIELD_ERRORS
from django.db.models import Q, QuerySet
from django.forms.utils import ErrorList
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls.base import reverse
from django.views.generic import FormView, ListView, TemplateView, UpdateView

from config.config import PROD_URL
from form.canvas import (
    get_base_url,
    get_canvas_user_by_pennkey,
    get_current_term,
    get_next_term,
)
from form.templatetags.template_filters import get_term
from form.terms import CURRENT_TERM, NEXT_TERM
from form.utils import get_sort_value

from .forms import AutoAddForm, RequestForm, SectionEnrollmentForm, SyncSectionForm
from .models import (
    AutoAdd,
    Enrollment,
    Request,
    School,
    Section,
    SectionEnrollment,
    User,
)

HOME_LIST_LIMIT = 10
HOME_LIST_INCREMENT = 5
SECTION_LIST_PAGINATE_BY = 30


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = "form/home.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        user = cast(User, self.request.user)
        sections = user.get_sections()
        sections_count = len(sections)
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
        context["current_term"] = get_current_term()
        context["next_term"] = get_next_term()
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
        context["source"] = "home"
        context["requests_sort"] = "status"
        context["sections_sort"] = "request__requester"
        context["canvas_sites_sort"] = "canvas_course_id"
        return context


class MyRequestsView(TemplateView):
    template_name = "form/my_requests.html"

    def get_sort_by_other_requester(self) -> Callable:
        user = cast(User, self.request.user)

        def sort_by_other_requester(section: Section) -> str:
            return section.get_other_requester(user)

        return sort_by_other_requester

    def get_sort_function(self, sort: str):
        sort = sort.replace("-", "")
        sort_functions = {
            "section__section_code": Request.get_request_section_code,
            "requester": self.get_sort_by_other_requester(),
            "created_at": Request.get_request_created_at,
            "status": Request.get_request_status,
        }
        return sort_functions.get(sort, Request.get_request_created_at)

    def sort_requests(
        self, requests: Union[QuerySet[Request], list[Request]], sort: str
    ) -> list[Request]:
        requests = list(requests)
        reverse = "-" in sort
        function = self.get_sort_function(sort)
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
            sort = "status"
        context["requests"] = requests
        context["sort_requests_section"] = get_sort_value("section__section_code", sort)
        context["sort_requests_created_at"] = get_sort_value(
            "created_at", sort, ascending=False
        )
        context["sort_requests_requester"] = get_sort_value("requester", sort)
        context["sort_requests_status"] = get_sort_value("status", sort)
        context["limit_requests"] = limit
        context["load_more_requests"] = requests_count > limit
        context["requests_sort"] = sort
        return context


class MyCoursesView(TemplateView):
    template_name = "form/section_list_table.html"

    def get_sort_by_other_requester(self) -> Callable:
        user = cast(User, self.request.user)

        def sort_by_other_requester(section: Section) -> str:
            return section.get_other_requester(user)

        return sort_by_other_requester

    def get_sort_function(self, sort: str):
        sort = sort.replace("-", "")
        sort_functions = {
            "section_code": Section.get_section_section_code,
            "title": Section.get_section_title,
            "schedule_type": Section.get_section_schedule_type,
            "instructors": Section.get_section_sortable_instructor,
            "request__requester": self.get_sort_by_other_requester(),
            "request__created_at": Section.get_section_request_created_at,
        }
        return sort_functions.get(sort, Section.get_section_request_created_at)

    def sort_sections(
        self, sections: Union[QuerySet[Section], list[Section]], sort: str
    ) -> list[Section]:
        sections = list(sections)
        reverse = "-" in sort
        function = self.get_sort_function(sort)
        sort_by_request = "request__requester" in sort or "request__created_at" in sort
        if sort_by_request:
            unrequested_sections = [
                section for section in sections if not section.get_request()
            ]
            requested_sections = [
                section for section in sections if section.get_request()
            ]
            requested_sections.sort(key=function, reverse=reverse)
            if reverse:
                sections = unrequested_sections + requested_sections
            else:
                sections = requested_sections + unrequested_sections
        else:
            sections.sort(key=function, reverse=reverse)
        return sections

    @staticmethod
    def get_term_code(term: str) -> Optional[int]:
        if not term:
            return None
        return int(term.split(" ")[0])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        source = self.request.GET.get("source", "sections")
        term = self.request.GET.get("term", "")
        context["term"] = term
        term = self.get_term_code(term)
        status = self.request.GET.get("status", "")
        if source == "home":
            user = cast(User, self.request.user)
            sections = user.get_sections(term)
            if status == "requested":
                sections = [section for section in sections if section.get_request()]
            elif status == "unrequested":
                sections = [
                    section for section in sections if not section.get_request()
                ]
        else:
            sections = list(Section.objects.filter(primary_section__isnull=True))
        sections_count = len(sections)
        limit = self.request.GET.get("limit", HOME_LIST_LIMIT)
        limit = int(limit) if limit else 0
        sort = self.request.GET.get("sort", "")
        if sort:
            if limit:
                sections = sections[:limit]
            sections = self.sort_sections(sections, sort)
        elif limit:
            limit = limit + HOME_LIST_INCREMENT
            sections = sections[:limit]
            sort = "request__requester"
        context["sections"] = (
            sections[:limit] if limit else sections[:SECTION_LIST_PAGINATE_BY]
        )
        context["sort_sections_section"] = get_sort_value(
            "section_code", sort, ascending=False
        )
        context["sort_sections_title"] = get_sort_value("title", sort)
        context["sort_sections_schedule_type"] = get_sort_value("schedule_type", sort)
        context["sort_sections_instructors"] = get_sort_value("instructors", sort)
        context["sort_sections_requester"] = get_sort_value("request__requester", sort)
        context["sort_sections_created_at"] = get_sort_value(
            "request__created_at", sort
        )
        context["limit_sections"] = limit
        context["load_more_sections"] = sections_count > limit if limit else False
        context["sections_sort"] = sort
        context["source"] = source
        context["status_filter"] = status
        context["current_term"] = get_current_term()
        context["next_term"] = get_next_term()
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
    def get_sort_function(cls, sort: str):
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
            sort = "canvas_course_id"
        context["canvas_sites"] = canvas_sites[:limit] if canvas_sites else []
        context["sort_canvas_sites_course_id"] = get_sort_value("course_id", sort)
        context["sort_canvas_sites_name"] = get_sort_value("name", sort)
        context["sort_canvas_sites_term"] = get_sort_value("term", sort)
        context["sort_canvas_sites_canvas_course_id"] = get_sort_value(
            "canvas_course_id", sort
        )
        context["limit_canvas_sites"] = limit
        context["load_more_canvas_sites"] = canvas_sites_count > limit
        context["canvas_sites_sort"] = sort
        return context


class SectionListView(ListView):
    model = Section
    paginate_by = SECTION_LIST_PAGINATE_BY
    context_object_name = "sections"

    @staticmethod
    def get_request_isnull(status):
        request_isnull_statues = {"requested": False, "unrequested": True}
        return request_isnull_statues.get(status)

    def get_queryset(self):
        request = self.request.GET
        sections = Section.objects.filter(
            primary_section__isnull=True, school__visible=True
        )
        clear = request.get("clear")
        if clear:
            return sections
        term = request.get("term")
        status = request.get("status")
        sort = request.get("sort")
        search = request.get("search")
        if term == get_current_term():
            sections = sections.filter(term=CURRENT_TERM)
        elif term == get_next_term():
            sections = sections.filter(term=NEXT_TERM)
        if status:
            request_isnull = self.get_request_isnull(status)
            sections = sections.filter(request__isnull=request_isnull)
        if sort:
            sections = sections.order_by(sort)
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
        context["current_term"] = get_current_term()
        context["next_term"] = get_next_term()
        context["term"] = term
        context["status_filter"] = status
        context["status"] = status
        context["search"] = search
        context["source"] = "sections"
        context["sections_sort"] = self.request.GET.get("sort", "") or "section_code"
        context["sort_sections_section"] = "-section_code"
        context["sort_sections_title"] = "title"
        context["sort_sections_schedule_type"] = "schedule_type"
        context["sort_sections_instructors"] = "instructors"
        context["sort_sections_requester"] = "request__requester"
        context["sort_sections_created_at"] = "request__created_at"
        context["sort_sections_status"] = "request__status"
        return context


class RequestDetailView(UpdateView):
    model = Request
    fields = "__all__"
    template_name = "form/request_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request.POST
        if "change_status" in request:
            new_status = request["change_status"]
            request_object = context["request"]
            request_object.set_status(new_status)
        status_choices = Request.Status.choices
        editable_choices = {"Submitted", "Approved", "Locked", "Canceled", "Completed"}
        status_choices = [
            choice[0] for choice in status_choices if choice[0] in editable_choices
        ]
        canvas_site_id, canvas_site_name = context["request"].get_canvas_site()
        context["canvas_site_id"] = canvas_site_id
        context["canvas_site_name"] = canvas_site_name
        context["canvas_site_url"] = f"{get_base_url()}/courses/{canvas_site_id}"
        context["status_choices"] = status_choices
        return context


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
        instructors = section.get_all_instructors()
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
        all_sections = [section]
        if included_sections:
            request.included_sections.set(included_sections)
            all_sections = all_sections + list(included_sections)
        for section in all_sections:
            section.set_requested(True)
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
        new_enrollment_count = values["rowCount"]
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
        enrollment_count = values["rowCount"]
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


class SyncSectionView(FormView):
    form_class = SyncSectionForm
    template_name = "form/sync_section.html"

    def form_valid(self, form):
        values = cast(dict, form.cleaned_data)
        subject = values["subject"]
        course_number = values["course_number"]
        section_number = values["section_number"]
        term = values["term"]
        section_id = f"{subject}{course_number}{section_number}"
        section = Section.sync_section(section_id=section_id, term=term)
        if not section:
            errors = form._errors.setdefault(NON_FIELD_ERRORS, ErrorList())
            errors.append("Course NOT FOUND. Please try again later.")
            return super().form_invalid(form)
        self.section_code = section.section_code
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("section_request", args=[self.section_code])


def create_canvas_site_view(request):
    section_code = request.GET["section_code"]
    request = Request.get_request(section_code)
    if not request:
        return redirect("request_detail", pk=section_code)
    request.create_canvas_site()
    return redirect("request_detail", pk=section_code)


class LookUpUserView(TemplateView):
    template_name = "form/look_up_user.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request.GET
        if "pennkey" not in request:
            return context
        pennkey = self.request.GET["pennkey"]
        context["pennkey"] = pennkey
        user = User.get_user(pennkey)
        if user:
            context["penn_id"] = user.penn_id
            context["email"] = user.email
            context["sections"] = user.get_sections()
            context["requests"] = user.get_requests()
            context["canvas_sites"] = user.get_canvas_sites()
        canvas_user = get_canvas_user_by_pennkey(pennkey)
        context["canvas_base_url"] = f"{get_base_url()}/courses/"
        if canvas_user:
            context["canvas_user_id"] = canvas_user.id
            context["canvas_user_name"] = canvas_user.name
        return context


class SchoolListView(ListView):
    model = School
    fields = "__all__"
    template_name = "form/schools.html"
    context_object_name = "schools"


class ToggleSchoolView(TemplateView):
    template_name = "form/school_row.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        school_code = self.request.GET["school_code"]
        school = School.get_school(school_code)
        if school:
            school.toggle_visible()
            context["school"] = school
        return context


class AutoAddListView(ListView):
    model = AutoAdd
    fields = "__all__"
    template_name = "form/auto_add.html"
    context_object_name = "auto_adds"


class AutoAddCreateView(TemplateView):
    template_name = "form/auto_add_form.html"

    @staticmethod
    def get_pennkey(user_display: str) -> str:
        pennkey_start = user_display.find("(") + 1
        pennkey_end = user_display.find(")")
        return user_display[pennkey_start:pennkey_end]

    @staticmethod
    def get_role(role: str) -> str:
        return AutoAdd.CanvasRole[role.upper()].name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        values = self.request.GET
        print(values)
        new_row_count = values["rowCount"]
        editing = "pennkey" in values and "role" in values
        if editing:
            pennkey = self.get_pennkey(values["pennkey"])
            role = self.get_role(values["role"])
            form_data = {
                "user": pennkey,
                "role": role,
            }
            form = AutoAddForm(form_data)
            form.auto_id = f"id_%s_{new_row_count}"
        else:
            new_row_count = int(new_row_count) + 1
            form = AutoAddForm(auto_id=f"id_%s_{new_row_count}")
        div_id = f"id_create_auto_add_{new_row_count}"
        button_id = f"id_load_user_{new_row_count}"
        remove_button_id = f"id_remove_{new_row_count}"
        context["div_id"] = div_id
        context["button_id"] = button_id
        context["remove_button_id"] = remove_button_id
        context["form"] = form
        return context
