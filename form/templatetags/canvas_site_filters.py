from functools import lru_cache

from django import template

from form.canvas import get_canvas_enrollment_term_name

register = template.Library()


@lru_cache
def get_term(enrollment_term_id: int) -> str:
    return get_canvas_enrollment_term_name(enrollment_term_id)


register.filter("get_term", get_term)
