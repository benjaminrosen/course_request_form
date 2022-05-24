from typing import cast
from functools import reduce
from django.views.generic import DetailView, ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from config.config import PROD_URL
from django.db.models import Q

from form.canvas import get_user_canvas_sites

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
        current = self.request.GET.get("202220")
        next_term = self.request.GET.get("202230")
        search = self.request.GET.get("search")
        sections = Section.objects.filter(primary_section__isnull=True)
        if current and not next_term:
            sections = sections.filter(term=202220)
        elif next_term and not current:
            sections = sections.filter(term=202230)
        if search:
            search = search.split()
            sections = sections.filter(
                reduce(
                    lambda first, second: first | second,
                    [
                        Q(section_code__icontains=search_term)
                        | Q(title__icontains=search_term)
                        for search_term in search
                    ],
                )
            )
        return sections


class SectionDetailView(DetailView):
    model = Section
