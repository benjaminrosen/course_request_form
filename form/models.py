from logging import getLogger

from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, EmailField, IntegerField, Model

from canvas.canvas_api import get_canvas_user_id_by_pennkey
from data_warehouse.data_warehouse import execute_query

logger = getLogger(__name__)


class User(AbstractUser):
    penn_id = IntegerField(unique=True, null=True)
    email_address = EmailField(unique=True, null=True)
    canvas_id = IntegerField(unique=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

    @staticmethod
    def log_field(username: str, field: str, value):
        if value:
            logger.info(f"FOUND {field} '{value}' for {username}")
        else:
            logger.warning(f"{field} NOT FOUND for {username}")

    def sync_dw_info(self, save=True):
        logger.info(f"Getting {self.username}'s info from Data Warehouse...")
        query = """
                SELECT
                    first_name, last_name, penn_id, email_address
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

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.sync_dw_info(save=False)
            self.sync_canvas_id(save=False)
        super().save(*args, **kwargs)


class ScheduleType(Model):
    sched_type_code = CharField(max_length=255, unique=True, primary_key=True)
    sched_type_desc = CharField(max_length=255)

    def __str__(self):
        return f"{self.sched_type_desc} ({self.sched_type_code})"

    @classmethod
    def sync(cls):
        query = "SELECT sched_type_code, sched_type_desc FROM dwngss.v_sched_type"
        cursor = execute_query(query)
        for sched_type_code, sched_type_desc in cursor:
            schedule_type, created = cls.objects.update_or_create(
                sched_type_code=sched_type_code,
                defaults={"sched_type_desc": sched_type_desc},
            )
            action = "ADDED" if created else "UPDATED"
            logger.info(f"{action} {schedule_type}")
