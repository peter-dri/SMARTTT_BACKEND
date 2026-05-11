"""
Student API views and viewsets.

Implements RESTful endpoints for student profile management,
enrollment tracking, and academic progress monitoring.
"""

from rest_framework import viewsets, status, generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _

from apps.students.models import Student, AcademicProgress, StudentEnrollment
from apps.students.serializers import (
    StudentListSerializer,
    StudentDetailSerializer,
    StudentCreateUpdateSerializer,
    StudentProfileUpdateSerializer,
    StudentMyProfileSerializer,
    AcademicProgressSerializer,
    StudentEnrollmentSerializer,
)
from apps.students.permissions import (
    CanManageStudents,
    CanViewStudentProfile,
    CanUpdateOwnProfile,
    CanViewAcademicProgress,
    CanManageEnrollments,
)
from apps.students.selectors import (
    StudentSelector,
    AcademicProgressSelector,
    StudentEnrollmentSelector,
)
from apps.students.services import (
    StudentProfileService,
    StudentEnrollmentService,
    StudentCurriculumService,
    StudentTimetableService,
    StudentAnalyticsService,
)
from apps.students.utils import is_super_admin, is_department_admin


class StudentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for student management.

    Provides CRUD operations and specialized endpoints for:
    - Student profiles
    - Academic progress
    - Enrollments
    - Curriculum
    - Timetable
    """

    permission_classes = [IsAuthenticated, CanManageStudents]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'program', 'academic_status', 'is_active', 'admission_year']
    search_fields = ['registration_number', 'first_name', 'last_name', 'email']
    ordering_fields = ['registration_number', 'created_at', 'academic_status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Get appropriate serializer based on action."""
        if self.action == 'list':
            return StudentListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return StudentCreateUpdateSerializer
        else:
            return StudentDetailSerializer

    def get_queryset(self):
        """Get filtered queryset based on user role."""
        # Base queryset with optimizations
        queryset = StudentSelector.get_student_list()

        # Filter by department for department admins
        if is_department_admin(self.request.user) and not is_super_admin(self.request.user):
            department_id = getattr(self.request.user, 'department_id', None)
            if department_id:
                queryset = queryset.filter(department_id=department_id)

        return queryset

    def create(self, request, *args, **kwargs):
        """Create a new student profile."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            from apps.accounts.models import User
            from apps.departments.models import Department
            from apps.programs.models import Program

            user = User.objects.get(id=serializer.validated_data['user_id'])
            department = Department.objects.get(id=serializer.validated_data['department_id'])
            program = Program.objects.get(id=serializer.validated_data['program_id'])

            student = StudentProfileService.create_student(
                user=user,
                department=department,
                program=program,
                **{k: v for k, v in serializer.validated_data.items()
                   if k not in ['user_id', 'department_id', 'program_id']}
            )

            output_serializer = StudentDetailSerializer(student)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def partial_update(self, request, *args, **kwargs):
        """Partially update student profile."""
        student = self.get_object()
        serializer = self.get_serializer(student, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            updated_student = StudentProfileService.update_student_profile(
                student,
                **serializer.validated_data
            )

            output_serializer = StudentDetailSerializer(updated_student)
            return Response(output_serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='me',
        url_name='my-profile'
    )
    def my_profile(self, request):
        """Get logged-in student's own profile."""
        try:
            student = StudentProfileService.get_student_profile_by_user_id(request.user.id)
            if not student:
                return Response(
                    {'error': _('Student profile not found.')},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = StudentMyProfileSerializer(student)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[IsAuthenticated, CanViewAcademicProgress],
        url_path='academic-progress',
        url_name='academic-progress'
    )
    def academic_progress(self, request, pk=None):
        """Get student's academic progress history."""
        student = self.get_object()
        progress_records = AcademicProgressSelector.get_student_progress(student.id)

        page = self.paginate_queryset(progress_records)
        if page is not None:
            serializer = AcademicProgressSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = AcademicProgressSerializer(progress_records, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[IsAuthenticated, CanViewAcademicProgress],
        url_path='enrollments',
        url_name='enrollments'
    )
    def enrollments(self, request, pk=None):
        """Get student's enrollment history."""
        student = self.get_object()
        enrollments = StudentEnrollmentSelector.get_student_enrollments(student.id)

        page = self.paginate_queryset(enrollments)
        if page is not None:
            serializer = StudentEnrollmentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = StudentEnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[IsAuthenticated, CanViewStudentProfile],
        url_path='curriculum-units',
        url_name='curriculum-units'
    )
    def curriculum_units(self, request, pk=None):
        """Get student's required curriculum units."""
        student = self.get_object()

        try:
            units = StudentCurriculumService.get_student_curriculum_units(student)
            return Response({
                'curriculum': StudentCurriculumService.get_student_curriculum(student).id if StudentCurriculumService.get_student_curriculum(student) else None,
                'units': [
                    {
                        'id': str(unit.unit.id),
                        'code': unit.unit.code,
                        'name': unit.unit.name,
                        'is_core': unit.is_core,
                        'is_elective': unit.is_elective,
                        'credit_hours': unit.credit_hours,
                    }
                    for unit in units
                ]
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[IsAuthenticated, CanViewStudentProfile],
        url_path='timetable',
        url_name='timetable'
    )
    def timetable(self, request, pk=None):
        """
        Get student's personalized timetable.

        Placeholder for integration with timetable module.
        """
        student = self.get_object()

        try:
            timetable_context = StudentTimetableService.prepare_student_timetable_context(student)
            return Response(timetable_context)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='statistics',
        url_name='statistics'
    )
    def statistics(self, request):
        """Get student statistics."""
        try:
            # Filter by department for department admins
            department_id = None
            if is_department_admin(request.user) and not is_super_admin(request.user):
                department_id = getattr(request.user, 'department_id', None)

            stats = StudentAnalyticsService.get_student_statistics(department_id)
            return Response(stats)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class StudentProfileUpdateView(generics.UpdateAPIView):
    """
    Allow students to update their own limited profile information.
    """

    serializer_class = StudentProfileUpdateSerializer
    permission_classes = [IsAuthenticated, CanUpdateOwnProfile]

    def get_object(self):
        """Get the logged-in user's student profile."""
        try:
            return Student.objects.get(user_id=self.request.user.id)
        except Student.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        """Allow GET to retrieve current profile."""
        student = self.get_object()
        if not student:
            return Response(
                {'error': _('Student profile not found.')},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = StudentMyProfileSerializer(student)
        return Response(serializer.data)


class AcademicProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing academic progress.

    Read-only access for students to view their academic progress.
    """

    serializer_class = AcademicProgressSerializer
    permission_classes = [IsAuthenticated, CanViewAcademicProgress]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'academic_year', 'academic_status']
    ordering = ['-academic_year', '-semester']

    def get_queryset(self):
        """Get filtered academic progress."""
        queryset = AcademicProgress.objects.select_related(
            'student',
            'recorded_by',
        )

        # Filter by student if they're viewing their own
        student_id = self.request.query_params.get('student_id')
        if student_id:
            # Check permission
            try:
                student = Student.objects.get(id=student_id)
                if hasattr(self.request.user, 'student_profile') and self.request.user.student_profile == student:
                    queryset = queryset.filter(student_id=student_id)
                elif is_super_admin(self.request.user):
                    queryset = queryset.filter(student_id=student_id)
                elif is_department_admin(self.request.user):
                    department_id = getattr(self.request.user, 'department_id', None)
                    if department_id and student.department_id == department_id:
                        queryset = queryset.filter(student_id=student_id)
                    else:
                        queryset = queryset.none()
                else:
                    queryset = queryset.none()
            except Student.DoesNotExist:
                queryset = queryset.none()

        return queryset


class StudentEnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing student enrollments.
    """

    serializer_class = StudentEnrollmentSerializer
    permission_classes = [IsAuthenticated, CanManageEnrollments]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'curriculum', 'enrollment_status']
    ordering = ['-academic_year', '-semester']

    def get_queryset(self):
        """Get filtered enrollments."""
        queryset = StudentEnrollment.objects.select_related(
            'student',
            'curriculum',
        )

        # Filter by department for department admins
        if is_department_admin(self.request.user) and not is_super_admin(self.request.user):
            department_id = getattr(self.request.user, 'department_id', None)
            if department_id:
                queryset = queryset.filter(student__department_id=department_id)

        return queryset

    @action(
        detail=True,
        methods=['post'],
        url_path='withdraw',
        url_name='withdraw'
    )
    def withdraw_enrollment(self, request, pk=None):
        """Withdraw a student from enrollment."""
        enrollment = self.get_object()

        try:
            reason = request.data.get('reason', '')
            enrollment = StudentEnrollmentService.withdraw_enrollment(enrollment, reason)
            serializer = self.get_serializer(enrollment)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
