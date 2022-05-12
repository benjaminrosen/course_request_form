from functools import lru_cache
from logging import getLogger
from typing import Optional

from canvasapi import Canvas
from canvasapi.account import Account
from canvasapi.exceptions import CanvasException
from canvasapi.user import User as CanvasUser

from config.config import DEBUG_VALUE, PROD_KEY, PROD_URL, TEST_KEY, TEST_URL

logger = getLogger(__name__)
MAIN_ACCOUNT_ID = 96678


def get_canvas(test=DEBUG_VALUE) -> Canvas:
    return Canvas(TEST_URL if test else PROD_URL, TEST_KEY if test else PROD_KEY)


def get_canvas_main_account() -> Account:
    return get_canvas().get_account(MAIN_ACCOUNT_ID)


@lru_cache
def get_all_canvas_accounts() -> list[Account]:
    return list(get_canvas_main_account().get_subaccounts(recursive=True))


def get_user_by_login_id(login_id: str) -> Optional[CanvasUser]:
    try:
        return get_canvas().get_user(login_id, "sis_login_id")
    except CanvasException:
        return None


def get_canvas_user_id_by_pennkey(login_id: str) -> Optional[int]:
    user = get_user_by_login_id(login_id)
    return user.id if user else None
