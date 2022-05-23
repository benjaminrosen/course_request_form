from django.views.generic import DetailView, ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Section


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = "form/home.html"


class SectionListView(ListView):
    model = Section


class SectionDetailView(DetailView):
    model = Section
