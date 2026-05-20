"""
Student services module.

Service layer containing all business logic related to students.
This layer coordinates between the API/views and the database layer,
handling complex operations and business rule enforcement.
"""

from typing import Optional, List, Dict
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.students.models import Student, AcademicProgress, StudentEnrollment
from apps.students.selectors import StudentSelector, AcademicProgressSelector, StudentEnrollmentSelector
from apps.students.validators import StudentValidator, AcademicProgressValidator, StudentEnrollmentValidator


class StudentProfileService:
    """
    Handles student profile operations.

    Responsibilities:
    - Create student profiles
    - Update student information
    - Retrieve student profiles
    - Maintain profile consistency
    """

    @staticmethod
    @transaction.atomic
    def create_student(
        user,
        registration_number: str,
        first_name: str,
        last_name: str,
        email: str,
        department,
        program,
        admission_year: int,
        current_study_year: int = 1,
        current_semester: int = 1,
        **extra_fields
    ) -> Student:
        """
        Create a new student profile.

        Args:
            user: User instance
            registration_number: Unique registration number
            first_name: Student's first name
            last_name: Student's last name
            email: Student's email
            department: Department instance
            program: Program instance
            admission_year: Year of admission
            current_study_year: Current study year
            current_semester: Current semester
            **extra_fields: Additional fields (phone_number, gender, etc.)

        Returns:
            Created Student instance

        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        StudentValidator.validate_registration_number_unique(registration_number)
        StudentValidator.validate_email_unique(email)
        StudentValidator.validate_admission_year(admission_year)
        StudentValidator.validate_study_year(current_study_year, program)
        StudentValidator.validate_semester(current_semester)
        StudentValidator.validate_department_program_match(department, program)

        # Create student
        student = Student.objects.create(
            user=user,
            registration_number=registration_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            department=department,
            program=program,
            admission_year=admission_year,
            current_study_year=current_study_year,
            current_semester=current_semester,
            **extra_fields
        )

        return student

    @staticmethod
    @transaction.atomic
    def update_student_profile(student: Student, **update_fields) -> Student:
        """
        Update student profile information.

        Args:
            student: Student instance to update
            **update_fields: Fields to update

        Returns:
            Updated Student instance

        Raises:
            ValidationError: If update is invalid
        """
        # Check if student can be updated
        StudentValidator.validate_student_can_update_profile(student)

        # Validate specific fields if present
        if "registration_number" in update_fields:
            StudentValidator.validate_registration_number_unique(
                update_fields["registration_number"],
                exclude_student_id=student.id
            )

        if "email" in update_fields:
            StudentValidator.validate_email_unique(
                update_fields["email"],
                exclude_student_id=student.id
            )

        if "current_study_year" in update_fields:
            StudentValidator.validate_study_year(
                update_fields["current_study_year"],
                student.program
            )

        if "current_semester" in update_fields:
            StudentValidator.validate_semester(update_fields["current_semester"])

        if "phone_number" in update_fields:
            StudentValidator.validate_phone_number(update_fields["phone_number"])

        # Update fields
        for field, value in update_fields.items():
            setattr(student, field, value)

        student.save()
        return student

    @staticmethod
    def get_student_profile(student_id) -> Optional[Student]:
        """
        Get complete student profile with relationships.

        Args:
            student_id: The student ID

        Returns:
            Student instance or None
        """
        return StudentSelector.get_student_by_id(student_id)

    @staticmethod
    def get_student_profile_by_registration_number(registration_number: str) -> Optional[Student]:
        """
        Get student by registration number.

        Args:
            registration_number: The registration number

        Returns:
            Student instance or None
        """
        return StudentSelector.get_student_by_registration_number(registration_number)

    @staticmethod
    def get_student_profile_by_user_id(user_id) -> Optional[Student]:
        """
        Get student profile by user ID.

        Args:
            user_id: The user ID

        Returns:
            Student instance or None
        """
        return StudentSelector.get_student_by_user_id(user_id)


class StudentCurriculumService:
    """
    Handles student curriculum operations.

    Responsibilities:
    - Determine student curriculum
    - Fetch required units
    - Connect with curriculum module
    - Prepare timetable filtering data
    """

    @staticmethod
    def get_student_curriculum(student: Student):
        """
        Get current curriculum for a student.

        Args:
            student: The student instance

        Returns:
            Curriculum instance or None
        """
        return student.get_current_curriculum()

    @staticmethod
    def get_student_curriculum_units(student: Student):
        """
        Get all units required by student's curriculum.

        Args:
            student: The student instance

        Returns:
            QuerySet of CurriculumUnits
        """
        curriculum = StudentCurriculumService.get_student_curriculum(student)
        if not curriculum:
            return []

        return curriculum.curriculum_units.all()

    @staticmethod
    def get_core_units(student: Student):
        """
        Get core (mandatory) units for student.

        Args:
            student: The student instance

        Returns:
            QuerySet of core units
        """
        curriculum = StudentCurriculumService.get_student_curriculum(student)
        if not curriculum:
            return []

        return curriculum.curriculum_units.filter(is_core=True)

    @staticmethod
    def get_elective_units(student: Student):
        """
        Get elective units for student.

        Args:
            student: The student instance

        Returns:
            QuerySet of elective units
        """
        curriculum = StudentCurriculumService.get_student_curriculum(student)
        if not curriculum:
            return []

        return curriculum.curriculum_units.filter(is_elective=True)

    @staticmethod
    def get_unit_prerequisites(student: Student):
        """
        Get unit prerequisites for student's curriculum.

        Args:
            student: The student instance

        Returns:
            Dictionary mapping units to prerequisites
        """
        curriculum_units = StudentCurriculumService.get_student_curriculum_units(student)
        prerequisites = {}

        for cu in curriculum_units:
            if cu.prerequisite_unit:
                prerequisites[cu.unit.code] = cu.prerequisite_unit.code

        return prerequisites


class StudentEnrollmentService:
    """
    Handles student enrollment operations.

    Responsibilities:
    - Manage semester enrollments
    - Track academic progression
    - Manage active enrollments
    - Handle enrollment status changes
    """

    @staticmethod
    @transaction.atomic
    def enroll_student(
        student: Student,
        curriculum,
        academic_year: str,
        study_year: int,
        semester: int
    ) -> StudentEnrollment:
        """
        Enroll student in a curriculum for a period.

        Args:
            student: The student instance
            curriculum: The curriculum instance
            academic_year: Academic year string (e.g., '2024/2025')
            study_year: Year of study
            semester: Semester (1 or 2)

        Returns:
            Created StudentEnrollment instance

        Raises:
            ValidationError: If enrollment is invalid
        """
        # Validate student can enroll
        StudentValidator.validate_student_can_enroll(student)

        # Validate curriculum matches student
        StudentEnrollmentValidator.validate_curriculum_program_match(student, curriculum)
        StudentEnrollmentValidator.validate_curriculum_year_match(curriculum, study_year)
        StudentEnrollmentValidator.validate_curriculum_semester_match(curriculum, semester)

        # Check for existing active enrollment for this period
        existing = StudentEnrollmentSelector.get_current_period_enrollment(
            student.id,
            academic_year,
            semester
        )
        if existing:
            raise ValidationError(
                _("Student already has an enrollment for this period.")
            )

        # Create enrollment
        enrollment = StudentEnrollment.objects.create(
            student=student,
            curriculum=curriculum,
            academic_year=academic_year,
            study_year=study_year,
            semester=semester,
            enrollment_status=StudentEnrollment.EnrollmentStatus.ENROLLED
        )

        return enrollment

    @staticmethod
    @transaction.atomic
    def withdraw_enrollment(
        enrollment: StudentEnrollment,
        reason: str = ""
    ) -> StudentEnrollment:
        """
        Withdraw a student from enrollment.

        Args:
            enrollment: The enrollment instance
            reason: Reason for withdrawal

        Returns:
            Updated enrollment instance

        Raises:
            ValidationError: If withdrawal is invalid
        """
        # Validate can be withdrawn
        StudentEnrollmentValidator.validate_student_can_withdraw(enrollment)

        # Update enrollment
        enrollment.enrollment_status = StudentEnrollment.EnrollmentStatus.WITHDRAWN
        enrollment.notes = reason
        enrollment.save()

        return enrollment

    @staticmethod
    @transaction.atomic
    def defer_enrollment(
        enrollment: StudentEnrollment,
        reason: str = ""
    ) -> StudentEnrollment:
        """
        Defer enrollment to next semester.

        Args:
            enrollment: The enrollment instance
            reason: Reason for deferral

        Returns:
            Updated enrollment instance
        """
        enrollment.enrollment_status = StudentEnrollment.EnrollmentStatus.DEFERRED
        enrollment.notes = reason
        enrollment.save()

        return enrollment

    @staticmethod
    def get_student_active_enrollment(student: Student) -> Optional[StudentEnrollment]:
        """
        Get current active enrollment.

        Args:
            student: The student instance

        Returns:
            Active StudentEnrollment or None
        """
        return StudentEnrollmentSelector.get_active_enrollment(student.id)

    @staticmethod
    def get_student_enrollments(student: Student):
        """
        Get all enrollments for student.

        Args:
            student: The student instance

        Returns:
            QuerySet of enrollments
        """
        return StudentEnrollmentSelector.get_student_enrollments(student.id)


class StudentTimetableService:
    """
    Handles integration with timetable module.

    Responsibilities:
    - Prepare timetable filtering data
    - Fetch personalized timetable
    - Connect with timetable module
    """

    @staticmethod
    def prepare_student_timetable_context(student: Student) -> Dict:
        """
        Prepare context for fetching student timetable.

        Returns data needed by timetable module to generate
        personalized timetable.

        Args:
            student: The student instance

        Returns:
            Dictionary with timetable context
        """
        curriculum = StudentCurriculumService.get_student_curriculum(student)
        enrollment = StudentEnrollmentService.get_student_active_enrollment(student)

        return {
            "student_id": str(student.id),
            "registration_number": student.registration_number,
            "program_id": str(student.program.id),
            "program_code": student.program.code,
            "department_id": str(student.department.id),
            "academic_year": student.academic_year_string,
            "study_year": student.current_study_year,
            "semester": student.current_semester,
            "curriculum_id": str(curriculum.id) if curriculum else None,
            "enrollment_id": str(enrollment.id) if enrollment else None,
            "units": [
                {
                    "id": str(cu.unit.id),
                    "code": cu.unit.code,
                    "name": cu.unit.name,
                    "is_core": cu.is_core,
                    "credit_hours": cu.credit_hours,
                }
                for cu in StudentCurriculumService.get_student_curriculum_units(student)
            ],
        }

    @staticmethod
    def get_student_timetable(student: Student):
        """
        Fetch personalized timetable for student.

        This is a placeholder for integration with the timetable module.
        The actual implementation will be in settings when timetable
        module is ready.

        Args:
            student: The student instance

        Returns:
            Timetable data (implementation depends on timetable module)
        """
        # TODO: Implement integration with timetable module
        # This will call timetable services with prepared context
        context = StudentTimetableService.prepare_student_timetable_context(student)
        return context


class StudentAnalyticsService:
    """
    Handles student analytics and reporting.

    Responsibilities:
    - Generate analytics data
    - Produce reports
    - Aggregate student metrics
    """

    @staticmethod
    def get_student_statistics(department_id: Optional[str] = None) -> Dict:
        """
        Get overall student statistics.

        Args:
            department_id: Filter by department (optional)

        Returns:
            Dictionary with statistics
        """
        status_counts = StudentSelector.count_students_by_status(department_id)
        active_count = StudentSelector.get_active_students(
            department_id=department_id
        ).count()

        return {
            "total_students": sum(status_counts.values()),
            "active_students": active_count,
            "by_status": status_counts,
        }

    @staticmethod
    def get_student_academic_progress_summary(student_id) -> Dict:
        """
        Get academic progress summary for student.

        Args:
            student_id: The student ID

        Returns:
            Dictionary with progress summary
        """
        latest = AcademicProgressSelector.get_latest_progress(student_id)

        if not latest:
            return {
                "gpa": 0.0,
                "cgpa": 0.0,
                "total_credits": 0,
                "status": "No records",
            }

        return {
            "gpa": float(latest.gpa),
            "cgpa": float(latest.cgpa),
            "total_credits": latest.total_credits,
            "status": latest.get_academic_status_display(),
            "academic_year": latest.academic_year,
            "semester": latest.semester,
        }
