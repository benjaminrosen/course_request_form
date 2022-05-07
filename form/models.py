from logging import getLogger

from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    EmailField,
    ForeignKey,
    IntegerField,
    Model,
)

from canvas.canvas_api import get_all_canvas_accounts, get_canvas_user_id_by_pennkey
from data_warehouse.data_warehouse import execute_query

logger = getLogger(__name__)


class User(AbstractUser):
    penn_id = IntegerField(unique=True, null=True)
    email_address = EmailField(unique=True, null=True)
    canvas_id = IntegerField(unique=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.sync_dw_info(save=False)
            self.sync_canvas_id(save=False)
        super().save(*args, **kwargs)

    @staticmethod
    def log_field(username: str, field: str, value):
        if value:
            logger.info(f"FOUND {field} '{value}' for {username}")
        else:
            logger.warning(f"{field} NOT FOUND for {username}")

    def sync_dw_info(self, save=True):
        logger.info(f"Getting {self.username}'s info from Data Warehouse...")
        query = """
                SELECT first_name, last_name, penn_id, email_address
                FROM employee_general
                WHERE pennkey = :username
                """
        cursor = execute_query(query, {"username": self.username})
        for first_name, last_name, penn_id, email_address in cursor:
            self.log_field(self.username, "first name", first_name)
            self.first_name = first_name.title() if first_name else ""
            self.log_field(self.username, "last name", last_name)
            self.last_name = last_name.title() if last_name else ""
            self.log_field(self.username, "Penn id", penn_id)
            self.penn_id = penn_id
            self.log_field(self.username, "email address", email_address)
            self.email_address = (
                email_address.strip().lower() if email_address else None
            )
        if save:
            self.save()

    def sync_canvas_id(self, save=True):
        logger.info(f"Getting {self.username}'s Canvas user id...")
        canvas_user_id = get_canvas_user_id_by_pennkey(self.username)
        self.log_field(self.username, "Canvas user id", canvas_user_id)
        if canvas_user_id:
            self.canvas_id = canvas_user_id
            if save:
                self.save()


class ScheduleType(Model):
    sched_type_code = CharField(max_length=255, unique=True, primary_key=True)
    sched_type_desc = CharField(max_length=255)

    def __str__(self):
        return f"{self.sched_type_desc} ({self.sched_type_code})"

    @classmethod
    def sync(cls):
        query = """
                SELECT sched_type_code, sched_type_desc
                FROM dwngss.v_sched_type
                """
        cursor = execute_query(query)
        for sched_type_code, sched_type_desc in cursor:
            schedule_type, created = cls.objects.update_or_create(
                sched_type_code=sched_type_code,
                defaults={"sched_type_desc": sched_type_desc},
            )
            action = "ADDED" if created else "UPDATED"
            logger.info(f"{action} {schedule_type}")


class School(Model):
    school_code = CharField(max_length=10, unique=True, primary_key=True)
    school_desc_long = CharField(max_length=50, unique=True)
    visible = BooleanField(default=True)
    canvas_sub_account_id = IntegerField(null=True)
    form_additional_enrollments = BooleanField(
        default=True, verbose_name="Additional Enrollments Form Field"
    )

    class Meta:
        ordering = ["school_desc_long"]

    def __str__(self):
        return f"{self.school_desc_long} ({self.school_code})"

    def save(self, *args, **kwargs):
        for subject in self.get_subjects():
            subject.visible = self.visible
            subject.save()
        super().save(*args, **kwargs)

    def get_subjects(self):
        return Subject.objects.filter(school=self)

    def get_canvas_sub_account(self):
        accounts = get_all_canvas_accounts()
        account_ids = (
            account.id for account in accounts if self.school_desc_long == account.name
        )
        account_id = next(account_ids, None)
        if account_id:
            self.canvas_sub_account_id = account_id
            self.save()

    @classmethod
    def create_school(cls, school_code: str, school_desc_long: str):
        school, created = cls.objects.update_or_create(
            school_code=school_code, defaults={"school_desc_long": school_desc_long}
        )
        school.get_canvas_sub_account()
        action = "ADDED" if created else "UPDATED"
        logger.info(f"{action} {school}")
        return school

    @classmethod
    def sync(cls):
        query = """
                SELECT school_code, school_desc_long
                FROM dwngss.v_school
                """
        cursor = execute_query(query)
        for school_code, school_desc_long in cursor:
            cls.create_school(school_code, school_desc_long)

    @classmethod
    def sync_school(cls, school_code: str):
        query = """
                SELECT school_code, school_desc_long
                FROM dwngss.v_school
                WHERE school_code = :school_code
                """
        cursor = execute_query(query, {"school_code": school_code})
        school = None
        for school_code, school_desc_long in cursor:
            school = cls.create_school(school_code, school_desc_long)
        return school


class Subject(Model):
    subject_code = CharField(max_length=10, unique=True, primary_key=True)
    subject_desc_long = CharField(max_length=255, null=True)
    visible = BooleanField(default=True)
    school = ForeignKey(
        School, related_name="subjects", on_delete=CASCADE, blank=True, null=True
    )

    class Meta:
        ordering = ["subject_desc_long"]

    def __str__(self):
        return f"{self.subject_desc_long} ({self.subject_code})"

    @classmethod
    def sync(cls):
        query = """
                SELECT subject_code, subject_desc_long, school_code
                FROM dwngss.v_subject
                """
        cursor = execute_query(query)
        for subject_code, subject_desc_long, school_code in cursor:
            try:
                school = School.objects.get(school_code=school_code)
            except Exception:
                if school_code:
                    school = School.sync_school(school_code)
                else:
                    school = None
            subject, created = cls.objects.update_or_create(
                subject_code=subject_code,
                defaults={"subject_desc_long": subject_desc_long, "school": school},
            )
            action = "ADDED" if created else "UPDATED"
            logger.info(f"{action} {subject}")
