from functools import reduce
from typing import cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls.base import reverse
from django.views.generic import DetailView, FormView, ListView, TemplateView

from config.config import PROD_URL
from form.canvas import get_user_canvas_sites
from form.terms import CURRENT_TERM, NEXT_TERM

from .forms import EmailForm, RequestForm
from .models import School, Section, User


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = "form/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = cast(User, self.request.user)
        context["email"] = user.email
        context["courses"] = Section.objects.filter(instructors=user)
        context["canvas_sites"] = get_user_canvas_sites(user.username)
        context["canvas_url"] = f"{PROD_URL}/courses"
        return context


class SectionListView(ListView):
    model = Section
    paginate_by = 30

    def get_queryset(self):
        sections = Section.objects.filter(primary_section__isnull=True)
        clear = self.request.GET.get("clear")
        if clear:
            return sections
        term = self.request.GET.get("term")
        search = self.request.GET.get("search")
        if term == str(CURRENT_TERM):
            sections = sections.filter(term=CURRENT_TERM)
        elif term == str(NEXT_TERM):
            sections = sections.filter(term=NEXT_TERM)
        if search:
            search_terms = search.split()
            sections = sections.filter(
                reduce(
                    lambda a, b: a & b,
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
        return sections

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clear = self.request.GET.get("clear")
        if clear:
            term = search = ""
        else:
            term = self.request.GET.get("term")
            search = self.request.GET.get("search") or ""
        context["current_term"] = str(CURRENT_TERM)
        context["next_term"] = str(NEXT_TERM)
        context["search"] = search
        context["term"] = term
        return context


class SectionDetailView(DetailView):
    model = Section


class RequestFormView(FormView):
    form_class = RequestForm
    template_name = "form/section_request.html"

    def get_section(self):
        section_code = self.kwargs["pk"]
        return Section.objects.get(section_code=section_code)

    def get_initial(self):
        initial = super().get_initial()
        username = self.request.user.username
        user = User.objects.get(username=username)
        section = self.get_section()
        instructors = section.instructors.all()
        initial_values = dict()
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
        context["section"] = section
        context["user_is_instructor"] = user_is_instructor
        context["is_sas_section"] = is_sas_section
        return context

    def get_success_url(self):
        return reverse("sections")


class EmailFormView(FormView):
    form_class = EmailForm
    template_name = "form/email_update.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"username": self.request.user.username})
        return kwargs

    def form_valid(self, form):
        new_email = form.cleaned_data.get("new_email")
        username = form.cleaned_data.get("username")
        try:
            user = User.objects.get(username=username)
        except Exception:
            user = None
        if user:
            user.set_email(email=new_email)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("home")


class ContactInfoView(TemplateView):
    template_name = "form/contact_info.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = cast(User, self.request.user)
        context["email"] = user.email
        return context


class CopyFromCourseView(TemplateView):
    template_name = "form/copy_from_course.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.GET.get("proxy-requester")
        try:
            username = User.objects.get(id=user_id).username
        except Exception:
            username = None
        canvas_sites = list()
        if username:
            canvas_sites = RequestForm.get_instructor_canvas_sites(username=username)
        context["canvas_sites"] = canvas_sites
        return context
