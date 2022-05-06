from unittest.mock import patch

from django.test import TestCase

from form.models import ScheduleType, User

EXECUTE_QUERY = "form.models.execute_query"
GET_CANVAS_USER_ID_BY_PENNKEY = "form.models.get_canvas_user_id_by_pennkey"


class UserTest(TestCase):
    username = "testuser"
    first_name = "Test"
    last_name = "User"
    penn_id = 1234567
    email_address = "testuser@upenn.edu"
    canvas_id = 7654321
    new_first_name = "New"
    new_last_name = "User"
    new_penn_id = 1234568
    new_email_address = "testuser@upenn.edu"
    new_canvas_id = 7654322

    @classmethod
    def get_mock_data_warehouse_response(cls, new=False, blank=False):
        if new:
            return (
                (
                    cls.new_first_name.upper(),
                    cls.new_last_name.upper(),
                    cls.new_penn_id,
                    f"{cls.new_email_address}    ",
                ),
            )
        elif blank:
            return ((None, None, None, None),)
        else:
            return (
                (
                    cls.first_name.upper(),
                    cls.last_name.upper(),
                    cls.penn_id,
                    f"{cls.email_address}    ",
                ),
            )

    @classmethod
    def create_user(cls):
        return User.objects.create(
            username=cls.username, first_name=cls.first_name, last_name=cls.last_name
        )

    @patch(EXECUTE_QUERY)
    @patch(GET_CANVAS_USER_ID_BY_PENNKEY)
    def test_str(self, mock_get_canvas_user_id_by_pennkey, mock_execute_query):
        mock_execute_query.return_value = self.get_mock_data_warehouse_response()
        mock_get_canvas_user_id_by_pennkey.return_value = self.canvas_id
        user = self.create_user()
        user_string = str(user)
        user_first_and_last_and_username = (
            f"{self.first_name} {self.last_name} ({self.username})"
        )
        self.assertEqual(user_string, user_first_and_last_and_username)

    @patch(EXECUTE_QUERY)
    @patch(GET_CANVAS_USER_ID_BY_PENNKEY)
    def test_create_user(self, mock_get_canvas_user_id_by_pennkey, mock_execute_query):
        mock_execute_query.return_value = self.get_mock_data_warehouse_response()
        mock_get_canvas_user_id_by_pennkey.return_value = self.canvas_id
        user = User(username=self.username)
        empty_values = (
            user.first_name,
            user.last_name,
            user.penn_id,
            user.email_address,
            user.canvas_id,
        )
        self.assertFalse(any(empty_values))
        user.save()
        self.assertEqual(user.first_name, self.first_name)
        self.assertEqual(user.last_name, self.last_name)
        self.assertEqual(user.penn_id, self.penn_id)
        self.assertEqual(user.email_address, self.email_address)
        self.assertEqual(user.canvas_id, self.canvas_id)

    @patch(EXECUTE_QUERY)
    @patch(GET_CANVAS_USER_ID_BY_PENNKEY)
    def test_sync_dw_info(self, mock_get_canvas_user_id_by_pennkey, mock_execute_query):
        mock_execute_query.return_value = self.get_mock_data_warehouse_response()
        mock_get_canvas_user_id_by_pennkey.return_value = self.canvas_id
        user = self.create_user()
        mock_execute_query.return_value = self.get_mock_data_warehouse_response(
            new=True
        )
        user.sync_dw_info()
        self.assertEqual(user.first_name, self.new_first_name)
        self.assertEqual(user.last_name, self.new_last_name)
        self.assertEqual(user.penn_id, self.new_penn_id)
        self.assertEqual(user.email_address, self.new_email_address)
        mock_execute_query.return_value = self.get_mock_data_warehouse_response(
            blank=True
        )
        user.sync_dw_info()
        self.assertFalse(user.first_name)
        self.assertFalse(user.last_name)
        self.assertIsNone(user.penn_id)
        self.assertIsNone(user.email_address)

    @patch(EXECUTE_QUERY)
    @patch(GET_CANVAS_USER_ID_BY_PENNKEY)
    def test_sync_canvas_id(
        self, mock_get_canvas_user_id_by_pennkey, mock_execute_query
    ):
        mock_execute_query.return_value = self.get_mock_data_warehouse_response()
        mock_get_canvas_user_id_by_pennkey.return_value = self.canvas_id
        user = self.create_user()
        mock_execute_query.return_value = self.get_mock_data_warehouse_response(
            new=True
        )
        mock_get_canvas_user_id_by_pennkey.return_value = self.new_canvas_id
        user.sync_canvas_id()
        self.assertEqual(user.canvas_id, self.new_canvas_id)


class ScheduleTypeTest(TestCase):
    sched_type_code = "SCH"
    sched_type_desc = "Schedule Type Description"

    @classmethod
    def setUpTestData(cls):
        cls.schedule_type = ScheduleType.objects.create(
            sched_type_code=cls.sched_type_code, sched_type_desc=cls.sched_type_desc
        )

    def test_str(self):
        schedule_type_string = str(self.schedule_type)
        sched_type_desc_and_code = f"{self.sched_type_desc} ({self.sched_type_code})"
        self.assertEqual(schedule_type_string, sched_type_desc_and_code)

    def test_sync(self):
        mock_schedule_types = (
            ("ABC", f"First {self.sched_type_desc}"),
            ("EFG", f"Second {self.sched_type_desc}"),
            ("HIJ", f"Third {self.sched_type_desc}"),
        )
        schedule_type_count = ScheduleType.objects.count()
        self.assertEqual(schedule_type_count, 1)
        with patch("form.models.execute_query") as mock_execute_query:
            mock_execute_query.return_value = mock_schedule_types
            ScheduleType.sync()
        expected_schedule_type_count = len(mock_schedule_types) + schedule_type_count
        schedule_type_count = ScheduleType.objects.count()
        self.assertEqual(schedule_type_count, expected_schedule_type_count)
