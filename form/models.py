from logging import getLogger
from typing import Optional

from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKey,
    IntegerField,
    ManyToManyField,
    Model,
    OneToOneField,
    TextField,
)

from canvas.canvas_api import get_all_canvas_accounts, get_canvas_user_id_by_pennkey

from .data_warehouse import execute_query
from .terms import CURRENT_TERM

logger = getLogger(__name__)


class User(AbstractUser):
    penn_id = IntegerField(unique=True, null=True)
    canvas_id = IntegerField(unique=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

    def save(self, *args, **kwargs):
        if self._state.adding and not self.penn_id:
            self.sync_dw_info(save=False)
            self.sync_canvas_id(save=False)
        super().save(*args, **kwargs)

    @staticmethod
    def log_field(username: str, field: str, value):
        if value:
            logger.info(f"FOUND {field} '{value}' for '{username}'")
        else:
            logger.warning(f"{field} NOT FOUND for '{username}'")

    def sync_dw_info(self, save=True):
        logger.info(f"Getting {self.username}'s info from Data Warehouse...")
        query = """
                SELECT first_name, last_name, penn_id, email_address
                FROM employee_general
                WHERE pennkey = :username
                """
        cursor = execute_query(query, {"username": self.username})
        for first_name, last_name, penn_id, email in cursor:
            first_name = first_name.title() if first_name else ""
            self.log_field(self.username, "first name", first_name)
            self.first_name = first_name
            last_name = last_name.title() if last_name else ""
            self.log_field(self.username, "last name", last_name)
            self.last_name = last_name
            self.log_field(self.username, "Penn id", penn_id)
            self.penn_id = penn_id
            email = email.strip().lower() if email else None
            self.log_field(self.username, "email", email)
            self.email = email or ""

        if save:
            self.save()

    def sync_canvas_id(self, save=True):
        logger.info(f"Getting Canvas user id for '{self.username}'...")
        canvas_user_id = get_canvas_user_id_by_pennkey(self.username)
        self.log_field(self.username, "Canvas user id", canvas_user_id)
        if canvas_user_id:
            self.canvas_id = canvas_user_id
            if save:
                self.save()


class ScheduleType(Model):
    QUERY = """
            SELECT sched_type_code, sched_type_desc
            FROM dwngss.v_sched_type
            """
    sched_type_code = CharField(max_length=255, unique=True, primary_key=True)
    sched_type_desc = CharField(max_length=255)

    def __str__(self):
        return f"{self.sched_type_desc} ({self.sched_type_code})"

    @classmethod
    def update_or_create(cls, query: str, kwargs: Optional[dict] = None):
        cursor = execute_query(query, kwargs)
        schedule_type = None
        for sched_type_code, sched_type_desc in cursor:
            try:
                schedule_type, created = cls.objects.update_or_create(
                    sched_type_code=sched_type_code,
                    defaults={"sched_type_desc": sched_type_desc},
                )
                action = "ADDED" if created else "UPDATED"
                logger.info(f"{action} {schedule_type}")
            except Exception as error:
                logger.error(
                    f"FAILED to update or create schedule type '{sched_type_code}':"
                    f" {error}"
                )
        return schedule_type

    @classmethod
    def sync_all(cls):
        cls.update_or_create(cls.QUERY)

    @classmethod
    def sync_schedule_type(cls, sched_type_code: str):
        query = f"{cls.QUERY} WHERE sched_type_code = :sched_type_code"
        kwargs = {"sched_type_code": sched_type_code}
        return cls.update_or_create(query, kwargs)

    @classmethod
    def get_schedule_type(cls, sched_type_code: str):
        try:
            return cls.objects.get(sched_type_code=sched_type_code)
        except Exception:
            return cls.sync_schedule_type(sched_type_code)


class School(Model):
    QUERY = """
            SELECT school_code, school_desc_long
            FROM dwngss.v_school
            """
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
    def update_or_create(cls, query: str, kwargs: Optional[dict] = None):
        cursor = execute_query(query, kwargs)
        school = None
        for school_code, school_desc_long in cursor:
            try:
                school, created = cls.objects.update_or_create(
                    school_code=school_code,
                    defaults={"school_desc_long": school_desc_long},
                )
                school.get_canvas_sub_account()
                action = "ADDED" if created else "UPDATED"
                logger.info(f"{action} {school}")
            except Exception as error:
                logger.error(
                    f"FAILED to update or create school '{school_code}': {error}"
                )
        return school

    @classmethod
    def sync_all(cls):
        cls.update_or_create(cls.QUERY)

    @classmethod
    def sync_school(cls, school_code: str):
        query = f"{cls.QUERY} WHERE school_code = :school_code"
        kwargs = {"school_code": school_code}
        return cls.update_or_create(query, kwargs)

    @classmethod
    def get_school(cls, school_code: str):
        try:
            school = cls.objects.get(school_code=school_code)
        except Exception:
            school = cls.sync_school(school_code)
        return school


class Subject(Model):
    QUERY = """
            SELECT subject_code, subject_desc_long, school_code
            FROM dwngss.v_subject
            """
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
    def update_or_create(cls, query: str, kwargs: Optional[dict] = None):
        cursor = execute_query(query, kwargs)
        subject = None
        for subject_code, subject_desc_long, school_code in cursor:
            try:
                school = School.get_school(school_code)
                subject, created = cls.objects.update_or_create(
                    subject_code=subject_code,
                    defaults={"subject_desc_long": subject_desc_long, "school": school},
                )
                action = "ADDED" if created else "UPDATED"
                logger.info(f"{action} {subject}")
            except Exception as error:
                logger.error(
                    f"FAILED to update or create subject '{subject_code}': {error}"
                )
        return subject

    @classmethod
    def sync_all(cls):
        cls.update_or_create(cls.QUERY)

    @classmethod
    def sync_subject(cls, subject_code: str):
        query = f"{cls.QUERY} WHERE subject_code = :subject_code"
        kwargs = {"subject_code": subject_code}
        return cls.update_or_create(query, kwargs)

    @classmethod
    def get_subject(cls, subject_code: str):
        try:
            return cls.objects.get(subject_code=subject_code)
        except Exception:
            return cls.sync_subject(subject_code)


class Section(Model):
    RELATED_NAME = "sections"
    ACTIVE_SECTION_STATUS_CODE = "A"
    QUERY = """
            SELECT
                section_id || term,
                section_id,
                primary_section_id,
                school,
                subject,
                primary_subject,
                course_num,
                section_num,
                term,
                title,
                schedule_type,
                section_status,
                primary_course_id,
                course_id
            FROM dwngss_ps.crse_section section
            WHERE schedule_type NOT IN (
                'MED',
                'DIS',
                'FLD',
                'F01',
                'F02',
                'F03',
                'F04',
                'IND',
                'I01',
                'I02',
                'I03',
                'I04',
                'MST',
                'SRT'
            )
            AND school NOT IN ('W', 'L')
            AND term = :term
            """
    QUERY_SECTION_ID = f"{QUERY} AND section_id = :section_id"
    QUERY_RELATED_SECTIONS = """
                    SELECT section_id
                    FROM dwngss_ps.crse_section
                    WHERE term = :term
                    AND section_id != :section_id
                    """
    section_code = CharField(
        max_length=150, unique=True, primary_key=True, editable=False
    )
    section_id = CharField(max_length=150, editable=False)
    primary_section = ForeignKey("self", on_delete=CASCADE, blank=True, null=True)
    school = ForeignKey(School, on_delete=CASCADE, related_name=RELATED_NAME)
    subject = ForeignKey(Subject, on_delete=CASCADE, related_name=RELATED_NAME)
    primary_subject = ForeignKey(Subject, on_delete=CASCADE)
    course_num = CharField(max_length=4, blank=False)
    section_num = CharField(max_length=4, blank=False)
    term = IntegerField()
    title = CharField(max_length=250)
    schedule_type = ForeignKey(
        ScheduleType, on_delete=CASCADE, related_name=RELATED_NAME
    )
    instructors = ManyToManyField(User, blank=True, related_name=RELATED_NAME)
    primary_course_id = CharField(max_length=150)
    also_offered_as = ManyToManyField("self", blank=True)
    course_sections = ManyToManyField("self", blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return self.section_code

    def sync_instructors(self):
        query = """
                SELECT
                    employee.pennkey,
                    instructor.instructor_first_name,
                    instructor.instructor_last_name,
                    instructor.instructor_penn_id,
                    instructor.instructor_email
                FROM dwngss_ps.crse_sect_instructor instructor
                JOIN employee_general_v employee
                ON instructor.instructor_penn_id = employee.penn_id
                WHERE instructor.section_id = :section_id
                AND term = :term
                """
        kwargs = {"section_id": f"{self.section_id}", "term": self.term}
        cursor = execute_query(query, kwargs)
        instructors = list()
        for penn_key, first_name, last_name, penn_id, email in cursor:
            try:
                user, created = User.objects.update_or_create(
                    username=penn_key,
                    defaults={
                        "first_name": first_name,
                        "last_name": last_name,
                        "penn_id": penn_id,
                        "email": email,
                    },
                )
                if user:
                    instructors.append(user)
                action = "ADDED" if created else "UPDATED"
                logger.info(f"{action} {user}")
            except Exception as error:
                logger.error(
                    f"FAILED to update or create instructor '{penn_key}': {error}"
                )
        self.instructors.set(instructors)

    def get_related_sections(self, cursor) -> list:
        related_sections = list()
        for section_id in cursor:
            section_id = next(iter(section_id))
            section = self.get_section(
                section_id, self.term, sync_related_sections=False
            )
            if section:
                related_sections.append(section)
        return related_sections

    def sync_also_offered_as_sections(self):
        query = (
            f"{self.QUERY_RELATED_SECTIONS} AND primary_course_id = :primary_course_id"
            " AND section_num = :section_num"
        )
        term = self.term
        kwargs = {
            "term": term,
            "primary_course_id": self.primary_course_id,
            "section_num": self.section_num,
            "section_id": self.section_id,
        }
        cursor = execute_query(query, kwargs)
        also_offered_as_sections = self.get_related_sections(cursor)
        self.also_offered_as.set(also_offered_as_sections)

    def sync_course_sections(self):
        query = f"{self.QUERY_RELATED_SECTIONS} AND course_id = :course_id"
        term = self.term
        course_id = f"{self.subject}{self.course_num}"
        kwargs = {
            "term": term,
            "course_id": course_id,
        }
        cursor = execute_query(query, kwargs)
        course_sections = self.get_related_sections(cursor)
        self.course_sections.set(course_sections)

    @classmethod
    def delete_canceled_section(cls, section_code: str):
        try:
            section = cls.objects.get(section_code=section_code)
        except Exception:
            section = None
        if section:
            section.delete()

    @classmethod
    def update_or_create(
        cls,
        query: str,
        kwargs: Optional[dict] = None,
        sync_related_sections=True,
    ):
        cursor = execute_query(query, kwargs)
        section = None
        for (
            section_code,
            section_id,
            primary_section_id,
            school_code,
            subject_code,
            primary_subject_code,
            course_num,
            section_num,
            term,
            title,
            sched_type_code,
            section_status,
            primary_course_id,
            course_id,
        ) in cursor:
            if section_status != cls.ACTIVE_SECTION_STATUS_CODE:
                cls.delete_canceled_section(section_code)
                continue
            school = School.get_school(school_code)
            subject = Subject.get_subject(subject_code)
            primary_subject = Subject.get_subject(primary_subject_code) or subject
            schedule_type = ScheduleType.get_schedule_type(sched_type_code)
            if primary_section_id != section_id:
                primary_section = cls.get_section(primary_section_id, term)
            else:
                primary_section = None
            try:
                section, created = cls.objects.update_or_create(
                    section_code=section_code,
                    defaults={
                        "section_id": section_id,
                        "primary_section": primary_section,
                        "school": school,
                        "subject": subject,
                        "primary_subject": primary_subject,
                        "course_num": course_num,
                        "section_num": section_num,
                        "term": term,
                        "title": title,
                        "schedule_type": schedule_type,
                        "primary_course_id": primary_course_id or course_id,
                    },
                )
                action = "ADDED" if created else "UPDATED"
                logger.info(f"{action} {section}")
                section.sync_instructors()
                if sync_related_sections:
                    section.sync_also_offered_as_sections()
                    section.sync_course_sections()
            except Exception as error:
                logger.error(
                    f"FAILED to update or create section '{section_code}': {error}"
                )
        return section

    @classmethod
    def sync_all(cls, term: Optional[int] = None):
        term = term or CURRENT_TERM
        kwargs = {"term": term}
        cls.update_or_create(cls.QUERY, kwargs)

    @classmethod
    def sync_section(
        cls,
        section_id: str,
        term: Optional[int] = None,
        sync_related_sections=True,
    ):
        term = term or CURRENT_TERM
        kwargs = {"section_id": section_id, "term": term}
        return cls.update_or_create(cls.QUERY_SECTION_ID, kwargs, sync_related_sections)

    def sync(self):
        kwargs = {"section_id": self.section_id, "term": self.term}
        self.update_or_create(self.QUERY_SECTION_ID, kwargs)

    @classmethod
    def get_section(
        cls,
        section_id: str,
        term: Optional[int] = None,
        sync_related_sections=True,
    ):
        term = term or CURRENT_TERM
        try:
            return cls.objects.get(section_id=section_id, term=term)
        except Exception:
            return cls.sync_section(section_id, term, sync_related_sections)


class Request(Model):
    STATUSES = (
        ("COMPLETED", "Completed"),
        ("IN_PROCESS", "In Process"),
        ("CANCELED", "Canceled"),
        ("APPROVED", "Approved"),
        ("SUBMITTED", "Submitted"),
        ("LOCKED", "Locked"),
    )
    section = OneToOneField(Section, on_delete=CASCADE, primary_key=True)
    requester = ForeignKey(User, on_delete=CASCADE, related_name="requests")
    proxy_requester = ForeignKey(
        User, on_delete=CASCADE, null=True, blank=True, related_name="proxy_requests"
    )
    title_override = CharField(max_length=255, null=True, default=None, blank=True)
    copy_from_course = IntegerField(null=True, default=None, blank=True)
    reserves = BooleanField(default=False)
    lps_online = BooleanField(default=False, verbose_name="LPS Online")
    exclude_announcements = BooleanField(default=False)
    additional_instructions = TextField(blank=True, default=None, null=True)
    admin_additional_instructions = TextField(blank=True, default=None, null=True)
    process_notes = TextField(blank=True, default="")
    status = CharField(max_length=20, choices=STATUSES, default="SUBMITTED")
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return self.section.section_code


# CANVAS_ROLES = (
#     ("TA", "TA"),
#     ("INST", "Instructor"),
#     ("DES", "Designer"),
#     ("LIB", "Librarian"),
#     ("OBS", "Observer"),
# )


# class AdditionalEnrollment(Model):
#     user = ForeignKey(User, on_delete=CASCADE)
#     role = CharField(max_length=4, choices=CANVAS_ROLES, default="TA")
#     request = ForeignKey(
#         Request, related_name="additional_enrollments", on_delete=CASCADE,
#         default=None
#     )


# class AutoAdd(Model):
#     user = ForeignKey(User, on_delete=CASCADE, blank=False)
#     school = ForeignKey(School, on_delete=CASCADE, blank=False)
#     subject = ForeignKey(Subject, on_delete=CASCADE, blank=False)
#     role = CharField(max_length=4, choices=CANVAS_ROLES)
#     created_at = DateTimeField(auto_now_add=True, null=True, blank=True)

#     class Meta:
#         ordering = ("user__username",)
