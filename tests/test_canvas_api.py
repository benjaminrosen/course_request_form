from unittest.mock import patch
from canvasapi.exceptions import CanvasException
from canvasapi.user import User as CanvasUser

from django.test import TestCase

from canvas.canvas_api import (
    get_canvas,
    get_canvas_user_id_by_pennkey,
    get_user_by_login_id,
)
from config.config import PROD_KEY, PROD_URL, TEST_KEY, TEST_URL


class CanvasApiTest(TestCase):
    user_id = 1234567
    login_id = "testuser"

    def test_get_canvas(self):
        canvas = get_canvas()
        self.assertEqual(canvas._Canvas__requester.original_url, TEST_URL)
        self.assertEqual(canvas._Canvas__requester.access_token, TEST_KEY)
        canvas = get_canvas(test=False)
        self.assertEqual(canvas._Canvas__requester.original_url, PROD_URL)
        self.assertEqual(canvas._Canvas__requester.access_token, PROD_KEY)

    @patch("canvas.canvas_api.get_canvas")
    def test_get_user_by_login_id(self, mock_get_canvas):
        class MockCanvas:
            @staticmethod
            def get_user(login_id, login_type):
                if login_id == self.login_id and login_type == "sis_login_id":
                    return CanvasUser(None, {"login_id": login_id})
                else:
                    raise CanvasException("")

        mock_get_canvas.return_value = MockCanvas()
        user = get_user_by_login_id(self.login_id)
        self.assertIsInstance(user, CanvasUser)
        self.assertEqual(user.login_id, self.login_id)
        user = get_user_by_login_id("")
        self.assertIsNone(user)

    @patch("canvas.canvas_api.get_user_by_login_id")
    def test_get_canvas_user_id_by_pennkey(self, mock_get_user_by_login_id):
        mock_get_user_by_login_id.return_value = CanvasUser(
            None, {"id": self.user_id, "login_id": self.login_id}
        )
        user_id = get_canvas_user_id_by_pennkey(self.login_id)
        self.assertEqual(user_id, self.user_id)
        mock_get_user_by_login_id.return_value = None
        user_id = get_canvas_user_id_by_pennkey(self.login_id)
        self.assertIsNone(user_id)
