from django.views.generic import ListView
from .models import Section


class SectionListView(ListView):
    model = Section
