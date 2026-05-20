"""
Student validators module.

Provides validation logic for student data to maintain data integrity
and enforce business rules.
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from apps.students.models import Student


class StudentValidator:
    """Centralized validation logic for student operations."""

    @staticmethod
    def validate_registration_number_unique(registration_number: str, exclude_student_id=None) -> None:
        """
        Validate that registration number is unique.

        Args:
            registration_number: The registration number to check
            exclude_student_id: Student ID to exclude from check (for updates)

        Raises:
            ValidationError: If registration number is not unique
        """
        qs = Student.objects.filter(registration_number=registration_number)

        if exclude_student_id:
            qs = qs.exclude(id=exclude_student_id)

        if qs.exists():
            raise ValidationError(
                _("A student with registration number '%(reg_num)s' already exists."),
                code="duplicate_registration_number",
                params={"reg_num": registration_number},
            )

    @staticmethod
    def validate_email_unique(email: str, exclude_student_id=None) -> None:
        """
        Validate that email is unique.

        Args:
            email: The email to check
            exclude_student_id: Student ID to exclude from check (for updates)

        Raises:
            ValidationError: If email is not unique
        """
        qs = Student.objects.filter(email=email)

        if exclude_student_id:
            qs = qs.exclude(id=exclude_student_id)

        if qs.exists():
            raise ValidationError(
                _("A student with email '%(email)s' already exists."),
                code="duplicate_email",
                params={"email": email},
            )

    @staticmethod
    def validate_admission_year(admission_year: int) -> None:
        """
        Validate admission year is reasonable.

        Args:
            admission_year: The admission year to validate

        Raises:
            ValidationError: If year is invalid
        """
        current_year = timezone.now().year

        if admission_year > current_year:
            raise ValidationError(
                _("Admission year cannot be in the future."),
                code="invalid_admission_year",
            )

        if admission_year < 1900:
            raise ValidationError(
                _("Admission year must be after 1900."),
                code="invalid_admission_year",
            )

    @staticmethod
    def validate_study_year(study_year: int, program=None) -> None:
        """
        Validate study year is valid for program.

        Args:
            study_year: The study year to validate
            program: The program to validate against

        Raises:
            ValidationError: If study year is invalid
        """
        if study_year < 1:
            raise ValidationError(
                _("Study year must be at least 1."),
                code="invalid_study_year",
            )

        if program and study_year > program.duration_years:
            raise ValidationError(
                _("Study year cannot exceed program duration of %(duration)d years."),
                code="invalid_study_year",
                params={"duration": program.duration_years},
            )

    @staticmethod
    def validate_semester(semester: int) -> None:
        """
        Validate semester is valid (1 or 2).

        Args:
            semester: The semester to validate

        Raises:
            ValidationError: If semester is invalid
        """
        if semester not in [1, 2]:
            raise ValidationError(
                _("Semester must be 1 or 2, not %(semester)d."),
                code="invalid_semester",
                params={"semester": semester},
            )

    @staticmethod
    def validate_phone_number(phone_number: str) -> None:
        """
        Validate phone number format.

        Args:
            phone_number: The phone number to validate

        Raises:
            ValidationError: If phone number format is invalid
        """
        import re

        if phone_number:
            pattern = r"^\+?1?\d{9,15}$"
            if not re.match(pattern, phone_number):
                raise ValidationError(
                    _("Phone number must be in valid international format."),
                    code="invalid_phone_number",
                )

    @staticmethod
    def validate_gender(gender: str) -> None:
        """
        Validate gender choice.

        Args:
            gender: The gender to validate

        Raises:
            ValidationError: If gender is not valid
        """
        valid_choices = [choice[0] for choice in Student.Gender.choices]
        if gender and gender not in valid_choices:
            raise ValidationError(
                _("Invalid gender value: %(gender)s."),
                code="invalid_gender",
                params={"gender": gender},
            )

    @staticmethod
    def validate_enrollment_type(enrollment_type: str) -> None:
        """
        Validate enrollment type.

        Args:
            enrollment_type: The enrollment type to validate

        Raises:
            ValidationError: If enrollment type is invalid
        """
        valid_choices = [choice[0] for choice in Student.EnrollmentType.choices]
        if enrollment_type not in valid_choices:
            raise ValidationError(
                _("Invalid enrollment type: %(type)s."),
                code="invalid_enrollment_type",
                params={"type": enrollment_type},
            )

    @staticmethod
    def validate_academic_status(academic_status: str) -> None:
        """
        Validate academic status.

        Args:
            academic_status: The academic status to validate

        Raises:
            ValidationError: If academic status is invalid
        """
        valid_choices = [choice[0] for choice in Student.AcademicStatus.choices]
        if academic_status not in valid_choices:
            raise ValidationError(
                _("Invalid academic status: %(status)s."),
                code="invalid_academic_status",
                params={"status": academic_status},
            )

    @staticmethod
    def validate_department_program_match(department, program) -> None:
        """
        Validate that department matches program's department.

        Args:
            department: The department
            program: The program

        Raises:
            ValidationError: If department doesn't match program
        """
        if program and program.department != department:
            raise ValidationError(
                _("Department must match the program's department."),
                code="department_program_mismatch",
            )

    @staticmethod
    def validate_student_can_update_profile(student, *args, **kwargs) -> None:
        """
        Validate whether student can update their profile.

        Args:
            student: The student instance

        Raises:
            ValidationError: If student cannot update profile
        """
        # Students with certain statuses might have restricted updates
        restricted_statuses = [
            Student.AcademicStatus.WITHDRAWN,
            Student.AcademicStatus.GRADUATED,
        ]

        if student.academic_status in restricted_statuses:
            raise ValidationError(
                _("Cannot update profile for students with status: %(status)s."),
                code="cannot_update_profile",
                params={"status": student.get_academic_status_display()},
            )

    @staticmethod
    def validate_student_can_enroll(student) -> None:
        """
        Validate whether student can enroll in curriculum.

        Args:
            student: The student instance

        Raises:
            ValidationError: If student cannot enroll
        """
        if not student.can_enroll_in_courses():
            raise ValidationError(
                _("Student cannot enroll due to academic status or inactivity."),
                code="cannot_enroll",
            )


class AcademicProgressValidator:
    """Validation logic for academic progress records."""

    @staticmethod
    def validate_gpa_range(gpa: float) -> None:
        """
        Validate GPA is in valid range.

        Args:
            gpa: The GPA to validate

        Raises:
            ValidationError: If GPA is out of range
        """
        if gpa < 0 or gpa > 4.0:
            raise ValidationError(
                _("GPA must be between 0.00 and 4.00, not %(gpa).2f."),
                code="invalid_gpa",
                params={"gpa": gpa},
            )

    @staticmethod
    def validate_cgpa_range(cgpa: float) -> None:
        """
        Validate CGPA is in valid range.

        Args:
            cgpa: The CGPA to validate

        Raises:
            ValidationError: If CGPA is out of range
        """
        if cgpa < 0 or cgpa > 4.0:
            raise ValidationError(
                _("CGPA must be between 0.00 and 4.00, not %(cgpa).2f."),
                code="invalid_cgpa",
                params={"cgpa": cgpa},
            )

    @staticmethod
    def validate_credits_non_negative(credits: int) -> None:
        """
        Validate credits are non-negative.

        Args:
            credits: The credits to validate

        Raises:
            ValidationError: If credits are negative
        """
        if credits < 0:
            raise ValidationError(
                _("Credits cannot be negative."),
                code="negative_credits",
            )

    @staticmethod
    def validate_unique_period(student, academic_year: str, study_year: int, semester: int, exclude_id=None) -> None:
        """
        Validate no duplicate academic progress for a period.

        Args:
            student: The student instance
            academic_year: The academic year
            study_year: The year of study
            semester: The semester
            exclude_id: Record ID to exclude (for updates)

        Raises:
            ValidationError: If duplicate exists
        """
        from apps.students.models import AcademicProgress

        qs = AcademicProgress.objects.filter(
            student=student,
            academic_year=academic_year,
            study_year=study_year,
            semester=semester,
        )

        if exclude_id:
            qs = qs.exclude(id=exclude_id)

        if qs.exists():
            raise ValidationError(
                _("Academic progress record already exists for this period."),
                code="duplicate_academic_progress",
            )


class StudentEnrollmentValidator:
    """Validation logic for student enrollments."""

    @staticmethod
    def validate_curriculum_program_match(student, curriculum) -> None:
        """
        Validate curriculum belongs to student's program.

        Args:
            student: The student instance
            curriculum: The curriculum instance

        Raises:
            ValidationError: If curriculum doesn't match student's program
        """
        if curriculum.program != student.program:
            raise ValidationError(
                _("Curriculum must belong to student's program."),
                code="curriculum_program_mismatch",
            )

    @staticmethod
    def validate_curriculum_year_match(curriculum, study_year: int) -> None:
        """
        Validate curriculum study year matches enrollment year.

        Args:
            curriculum: The curriculum instance
            study_year: The study year

        Raises:
            ValidationError: If study years don't match
        """
        if curriculum.study_year != study_year:
            raise ValidationError(
                _("Curriculum study year must match enrollment study year."),
                code="curriculum_year_mismatch",
            )

    @staticmethod
    def validate_curriculum_semester_match(curriculum, semester: int) -> None:
        """
        Validate curriculum semester matches enrollment semester.

        Args:
            curriculum: The curriculum instance
            semester: The semester

        Raises:
            ValidationError: If semesters don't match
        """
        if curriculum.semester != semester:
            raise ValidationError(
                _("Curriculum semester must match enrollment semester."),
                code="curriculum_semester_mismatch",
            )

    @staticmethod
    def validate_student_can_withdraw(enrollment) -> None:
        """
        Validate enrollment can be withdrawn.

        Args:
            enrollment: The enrollment instance

        Raises:
            ValidationError: If enrollment cannot be withdrawn
        """
        if not enrollment.can_be_withdrawn():
            raise ValidationError(
                _("Cannot withdraw enrollment with status: %(status)s."),
                code="cannot_withdraw_enrollment",
                params={"status": enrollment.get_enrollment_status_display()},
            )
