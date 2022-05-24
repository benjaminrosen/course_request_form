from typing import cast
from functools import reduce
from django.views.generic import DetailView, ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from config.config import PROD_URL
from django.db.models import Q

from form.canvas import get_user_canvas_sites
from form.terms import CURRENT_TERM, NEXT_TERM

from .models import Section, User


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
                        | Q(title__icontains=search_term)
                        | Q(schedule_type__sched_type_code__icontains=search_term)
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
            search = self.request.GET.get("search")
        context["current_term"] = str(CURRENT_TERM)
        context["next_term"] = str(NEXT_TERM)
        context["search"] = search
        context["term"] = term
        return context


class SectionDetailView(DetailView):
    model = Section
