from dataclasses import dataclass
from unittest.mock import patch

from django.test import TestCase

from form.models import ScheduleType, School, Subject, User

EXECUTE_QUERY = "form.models.execute_query"
GET_CANVAS_USER_ID_BY_PENNKEY = "form.models.get_canvas_user_id_by_pennkey"
GET_ALL_CANVAS_ACCOUNTS = "form.models.get_all_canvas_accounts"
SCHOOL_CODE = "SCHL"
SCHOOL_DESC_LONG = "School Description"
SUBJECT_CODE = "SUBJ"
SUBJECT_DESC_LONG = "Subject Description"


def get_mock_code_and_description(model: str) -> tuple:
    description = "Description"
    return (
        ("ABCD", f"First {model} {description}"),
        ("EFGH", f"Second {model} {description}"),
        ("IJKL", f"Third {model} {description}"),
        (None, None),
    )


def get_mock_values_success_count(values: tuple) -> int:
    success_values = [value for value in values if all(value)]
    return len(success_values)


class UserTest(TestCase):
    username = "testuser"
    first_name = "Test"
    last_name = "User"
    penn_id = 1234567
    email_address = "testuser@upenn.edu"
    canvas_id = 7654321
    new_first_name = "New"
    new_last_name = "Name"
    new_penn_id = 1234568
    new_email_address = "newname@upenn.edu"
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

    @patch(EXECUTE_QUERY)
    def test_sync_all(self, mock_execute_query):
        schedule_type_count = ScheduleType.objects.count()
        self.assertEqual(schedule_type_count, 1)
        mock_schedule_types = get_mock_code_and_description("Schedule Type")
        mock_execute_query.return_value = mock_schedule_types
        ScheduleType.sync_all()
        success_schedule_type_count = get_mock_values_success_count(mock_schedule_types)
        expected_schedule_type_count = success_schedule_type_count + schedule_type_count
        schedule_type_count = ScheduleType.objects.count()
        self.assertEqual(schedule_type_count, expected_schedule_type_count)


@dataclass
class MockAccount:
    id: int
    name: str


class SchoolTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.school = School.objects.create(
            school_code=SCHOOL_CODE, school_desc_long=SCHOOL_DESC_LONG
        )

    def test_str(self):
        school_string = str(self.school)
        school_desc_and_code = f"{SCHOOL_DESC_LONG} ({SCHOOL_CODE})"
        self.assertEqual(school_string, school_desc_and_code)

    def test_save(self):
        school = self.school
        self.assertFalse(school.get_subjects())
        Subject.objects.create(
            subject_code=SUBJECT_CODE,
            subject_desc_long=SUBJECT_DESC_LONG,
            school=school,
        )
        school.save()
        subjects = school.get_subjects()
        subject = next(subject for subject in subjects)
        self.assertTrue(subjects)
        self.assertTrue(len(subjects), 1)
        self.assertEqual(subject.subject_code, SUBJECT_CODE)

    @patch(EXECUTE_QUERY)
    @patch(GET_ALL_CANVAS_ACCOUNTS)
    def test_sync_all(self, mock_get_all_canvas_accounts, mock_execute_query):
        school_count = School.objects.count()
        self.assertEqual(school_count, 1)
        mock_schools = get_mock_code_and_description("School")
        mock_execute_query.return_value = mock_schools
        mock_get_all_canvas_accounts.return_value = [
            MockAccount(id=1, name=f"First {SCHOOL_DESC_LONG}")
        ]
        School.sync_all()
        success_school_count = get_mock_values_success_count(mock_schools)
        expected_school_count = success_school_count + school_count
        school_count = School.objects.count()
        self.assertEqual(school_count, expected_school_count)


class SubjectTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.subject = Subject.objects.create(
            subject_code=SUBJECT_CODE, subject_desc_long=SUBJECT_DESC_LONG
        )

    def test_str(self):
        subject_string = str(self.subject)
        subject_desc_and_code = f"{SUBJECT_DESC_LONG} ({SUBJECT_CODE})"
        self.assertEqual(subject_string, subject_desc_and_code)

    @patch(EXECUTE_QUERY)
    @patch(GET_ALL_CANVAS_ACCOUNTS)
    def test_sync_all(self, mock_get_all_canvas_accounts, mock_execute_query):
        subject_count = Subject.objects.count()
        self.assertEqual(subject_count, 1)
        mock_subjects = (
            ("ABCD", f"First {SUBJECT_DESC_LONG}", SCHOOL_CODE),
            ("EFGH", f"Second {SUBJECT_DESC_LONG}", SCHOOL_CODE),
            ("IJKL", f"Third {SUBJECT_DESC_LONG}", ()),
        )
        mock_school = ((SCHOOL_CODE, SCHOOL_DESC_LONG),)
        mock_school_not_found = ((None, None),)
        mock_execute_query.side_effect = [
            mock_subjects,
            mock_school,
            mock_school_not_found,
        ]
        mock_get_all_canvas_accounts.return_value = [MockAccount(1, SCHOOL_DESC_LONG)]
        Subject.sync_all()
        expected_subject_count = len(mock_subjects) + subject_count
        subject_count = Subject.objects.count()
        self.assertEqual(subject_count, expected_subject_count)
