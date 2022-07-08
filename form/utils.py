from typing import Callable, Union

from .models import Section
from django.db.models import QuerySet

from form.models import Request, User


def reverse_order(sort: str):
    descending = "-" in sort
    if descending:
        return sort.replace("-", "")
    return f"-{sort}"


def get_sort_value(name: str, value: str, ascending: bool = True):
    not_match = not value or name not in value
    if not_match:
        default_order = "" if ascending else "-"
        return f"{default_order}{name}"
    return reverse_order(value)


def sort_queryset_by_function(
    queryset: Union[list, QuerySet[Union[Request, Section]]],
    function: Callable,
    reverse: bool,
) -> list[Union[Request, Section]]:
    queryset = list(queryset)
    queryset.sort(key=function, reverse=reverse)
    return queryset
