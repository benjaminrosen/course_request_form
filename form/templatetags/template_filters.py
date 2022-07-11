from functools import lru_cache

from django import template
from form.canvas import get_canvas_enrollment_term_name

register = template.Library()


@lru_cache
def get_term(enrollment_term_id: int) -> str:
    return get_canvas_enrollment_term_name(enrollment_term_id)


def get_sort_by_base(sort_by: str) -> str:
    return sort_by.replace("-", "")


register.filter("get_term", get_term)
register.filter("get_sort_by_base", get_sort_by_base)
