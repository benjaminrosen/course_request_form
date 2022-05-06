from unittest.mock import patch

from django.test import TestCase

from form.models import ScheduleType, User


class UserTest(TestCase):
    username = "testuser"
    first_name = "Test"
    last_name = "User"

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            username=cls.username, first_name=cls.first_name, last_name=cls.last_name
        )

    def test_str(self):
        user_string = str(self.user)
        user_first_and_last_and_username = (
            f"{self.first_name} {self.last_name} ({self.username})"
        )
        self.assertEqual(user_string, user_first_and_last_and_username)


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
