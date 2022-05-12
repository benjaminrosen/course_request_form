from functools import lru_cache
from logging import getLogger
from typing import Optional

from canvasapi import Canvas
from canvasapi.account import Account
from canvasapi.course import Course
from canvasapi.exceptions import CanvasException
from canvasapi.user import User as CanvasUser
from django.db.models.query import QuerySet

from config.config import DEBUG_VALUE, PROD_KEY, PROD_URL, TEST_KEY, TEST_URL

logger = getLogger(__name__)
MAIN_ACCOUNT_ID = 96678


def get_canvas() -> Canvas:
    url = TEST_URL if DEBUG_VALUE else PROD_URL
    key = TEST_KEY if DEBUG_VALUE else PROD_KEY
    return Canvas(url, key)


def get_canvas_account(account_id: int) -> Account:
    return get_canvas().get_account(account_id)


def get_canvas_main_account() -> Account:
    return get_canvas_account(MAIN_ACCOUNT_ID)


@lru_cache
def get_all_canvas_accounts() -> list[Account]:
    return list(get_canvas_main_account().get_subaccounts(recursive=True))


def get_canvas_user_by_login_id(login_id: str) -> Optional[CanvasUser]:
    try:
        return get_canvas().get_user(login_id, "sis_login_id")
    except CanvasException:
        return None


def get_canvas_user_id_by_pennkey(login_id: str) -> Optional[int]:
    user = get_canvas_user_by_login_id(login_id)
    return user.id if user else None


def get_canvas_enrollment_term_id(term: int) -> Optional[int]:
    term_name = str(term)
    account = get_canvas().get_account(MAIN_ACCOUNT_ID)
    enrollment_terms = account.get_enrollment_terms()
    enrollment_term_ids = (
        term.id for term in enrollment_terms if term_name in term.name
    )
    return next(enrollment_term_ids, None)


def create_course_section(name: str, sis_course_id: str, canvas_course: Course):
    course_section = {"name": name, "sis_section_id": sis_course_id}
    canvas_course.create_course_section(
        course_section=course_section, enable_sis_reactivation=True
    ),


def update_canvas_course(course: dict) -> Optional[Course]:
    sis_course_id = course["sis_course_id"]
    try:
        canvas_course = get_canvas().get_course(sis_course_id, use_sis_id=True)
        canvas_course.update(course=course)
        return canvas_course
    except Exception as error:
        logger.error(f"FAILED to create Canvas course '{sis_course_id}': {error}")
        return None


def update_or_create_canvas_course(course: dict, account_id: int) -> Optional[Course]:
    try:
        account = get_canvas_account(account_id)
        canvas_course = account.create_course(course=course)
        name = canvas_course.name
        sis_course_id = canvas_course.sis_course_id
        create_course_section(name, sis_course_id, canvas_course)
        return canvas_course
    except Exception:
        return update_canvas_course(course)


def create_related_sections(
    related_sections: QuerySet, title_override: str, canvas_course: Course
):
    for section in related_sections:
        name = section.get_canvas_name(title_override, related_section=True)
        sis_course_id = section.get_canvas_sis_id()
        create_course_section(name, sis_course_id, canvas_course)
