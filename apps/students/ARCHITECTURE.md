# Students Management Module - Architecture Documentation

## Overview

The Students module is the **academic identity layer** of the SMARTTT University Management System. It serves as the foundation for:

- Student profile management
- Academic progress tracking
- Curriculum-driven unit assignment
- Personalized timetable generation
- Role-based access control

## System Context

```
University Structure:
  ├── Faculty/College
  │   └── Department
  │       ├── Program (Degree/Diploma/Certificate)
  │       │   ├── Curriculum (per year/semester)
  │       │   │   └── CurriculumUnit
  │       │   │       ├── Unit (Course)
  │       │   │       └── Prerequisites
  │       │   └── Student
  │       │       ├── Academic Progress
  │       │       └── Enrollments
```

## Architecture Principles

### 1. Clean Architecture

The module follows layers of separation:

```
API Layer (Views/ViewSets)
    ↓
Service Layer (Business Logic)
    ↓
Selector Layer (Database Queries)
    ↓
Models (Data)
```

### 2. Modular Design

Each responsibility is isolated:

- **Models**: Data structure and validation
- **Serializers**: API request/response formatting
- **Views**: HTTP endpoint handling
- **Services**: Business logic orchestration
- **Selectors**: Query optimization
- **Validators**: Data validation rules
- **Permissions**: Access control
- **Utils**: Helper functions

### 3. No Business Logic in Views

All business logic lives in the Service layer:

```python
# ❌ BAD - Logic in view
def create(self, request):
    student = Student.objects.create(...)
    enrollment = StudentEnrollment.objects.create(...)
    return Response(student)

# ✅ GOOD - Logic in service
def create(self, request):
    student_data = request.data
    student = StudentProfileService.create_student(**student_data)
    return Response(StudentDetailSerializer(student).data)
```

## Module Structure

```
students/
├── models/
│   ├── __init__.py              # Exports: Student, AcademicProgress, StudentEnrollment
│   └── student.py               # All model definitions
│
├── serializers/
│   ├── __init__.py              # Exports all serializers
│   ├── serializers.py           # Comprehensive serializer classes
│   └── student_serializer.py    # Legacy/compatible serializer
│
├── views/
│   ├── __init__.py              # Exports all viewsets
│   ├── views.py                 # Main viewsets and views
│   └── student_viewset.py       # Legacy/base viewset
│
├── services/
│   └── __init__.py              # Service classes:
│                                 # - StudentProfileService
│                                 # - StudentCurriculumService
│                                 # - StudentEnrollmentService
│                                 # - StudentTimetableService
│                                 # - StudentAnalyticsService
│
├── selectors/
│   └── __init__.py              # Selector classes:
│                                 # - StudentSelector
│                                 # - AcademicProgressSelector
│                                 # - StudentEnrollmentSelector
│
├── validators/
│   ├── __init__.py              # Exports validators
│   └── student_validator.py     # Validation logic
│
├── permissions/
│   ├── __init__.py              # Exports permission classes
│   └── permissions.py           # Access control
│
├── utils/
│   └── __init__.py              # Helper functions
│
├── urls.py                       # URL routing
├── admin.py                      # Django admin configuration
├── apps.py                       # App configuration
├── tests/                        # Test files
└── migrations/                   # Database migrations
```

## Data Models

### 1. Student

**Purpose**: Core academic identity

```python
Student {
    id (UUID)
    
    # User Link
    user (OneToOneField) → User
    
    # Academic Identity
    registration_number (CharField, unique)
    
    # Personal
    first_name, last_name, email, phone_number
    gender, date_of_birth
    profile_photo (ImageField)
    
    # Academic Organization
    faculty (ForeignKey) → Department
    department (ForeignKey) → Department
    program (ForeignKey) → Program
    
    # Academic Progress
    current_study_year (1-based)
    current_semester (1 or 2)
    admission_year
    
    # Status
    academic_status (ACTIVE|INACTIVE|SUSPENDED|GRADUATED|WITHDRAWN|ON_LEAVE)
    enrollment_type (FULL_TIME|PART_TIME|DISTANCE_LEARNING|SANDWICH|BLOCK_RELEASE)
    is_active (Boolean)
    
    # Metadata
    created_at, updated_at
}
```

**Key Methods**:
- `get_full_name()` → Full name
- `get_current_curriculum()` → Curriculum for current year/semester
- `get_required_units()` → Units from current curriculum
- `academic_year_string` → "2024/2025"
- `can_enroll_in_courses()` → Boolean
- `is_graduated` → Boolean
- `is_suspended` → Boolean

**Indexes**:
```python
# Individual field indexes for queries
- registration_number
- email
- department + program
- academic_status + is_active
- admission_year
- current_study_year + current_semester
```

**Constraints**:
- Unique: registration_number, email
- Check: study_year >= 1
- Check: semester >= 1
- Check: admission_year >= 1900

### 2. AcademicProgress

**Purpose**: Track semester-wise academic performance

```python
AcademicProgress {
    id (UUID)
    
    student (ForeignKey) → Student
    
    academic_year (CharField)     # "2024/2025"
    study_year
    semester (1 or 2)
    
    gpa (Decimal 0.00-4.00)
    cgpa (Decimal 0.00-4.00)
    total_credits
    credits_this_semester
    
    academic_status
    recorded_by (ForeignKey) → User
    
    created_at, updated_at
}
```

**Unique Constraint**:
```python
(student, academic_year, study_year, semester)
```

### 3. StudentEnrollment

**Purpose**: Track which curriculum students follow per period

```python
StudentEnrollment {
    id (UUID)
    
    student (ForeignKey) → Student
    curriculum (ForeignKey) → Curriculum
    
    academic_year
    study_year
    semester
    
    enrollment_status 
    # (ENROLLED|COMPLETED|WITHDRAWN|FAILED|SUSPENDED|DEFERRED)
    
    enrollment_date
    notes (TextField)
    
    created_at, updated_at
}
```

**Unique Constraint**:
```python
(student, curriculum, academic_year, study_year, semester)
```

## Service Layer

### StudentProfileService

Handles student profile operations:

```python
create_student(
    user, registration_number, first_name, last_name, email,
    department, program, admission_year,
    current_study_year=1, current_semester=1, **extra_fields
) → Student

update_student_profile(student, **update_fields) → Student

get_student_profile(student_id) → Student
get_student_profile_by_registration_number(reg_num) → Student
get_student_profile_by_user_id(user_id) → Student
```

### StudentCurriculumService

Manages curriculum operations:

```python
get_student_curriculum(student) → Curriculum
get_student_curriculum_units(student) → QuerySet[CurriculumUnit]
get_core_units(student) → QuerySet[CurriculumUnit]
get_elective_units(student) → QuerySet[CurriculumUnit]
get_unit_prerequisites(student) → Dict[unit_code, prerequisite_code]
```

**Key Flow**:
```
Student
  ↓ (by program, year, semester)
Curriculum
  ↓ (contains)
CurriculumUnit (many)
  ↓ (references)
Unit (course)
```

### StudentEnrollmentService

Handles enrollments:

```python
enroll_student(
    student, curriculum, academic_year,
    study_year, semester
) → StudentEnrollment

withdraw_enrollment(enrollment, reason="") → StudentEnrollment
defer_enrollment(enrollment, reason="") → StudentEnrollment

get_student_active_enrollment(student) → StudentEnrollment
get_student_enrollments(student) → QuerySet
```

### StudentTimetableService

Prepares timetable data (placeholder for integration):

```python
prepare_student_timetable_context(student) → Dict
get_student_timetable(student) → TimetableData
```

**Context returned**:
```python
{
    "student_id": uuid,
    "registration_number": str,
    "program_id": uuid,
    "academic_year": "2024/2025",
    "study_year": 2,
    "semester": 1,
    "curriculum_id": uuid,
    "units": [
        {
            "id": uuid,
            "code": "CS101",
            "name": "Introduction to Programming",
            "is_core": True,
            "credit_hours": 3,
        }
    ]
}
```

### StudentAnalyticsService

Analytics and reporting:

```python
get_student_statistics(department_id=None) → Dict
get_student_academic_progress_summary(student_id) → Dict
```

## Selector Layer

Database query optimization layer:

### StudentSelector

```python
get_student_list(filters=None, search=None, ordering="-created_at") → QuerySet
get_student_by_id(student_id) → Student
get_student_by_registration_number(reg_num) → Student
get_student_by_user_id(user_id) → Student

get_students_by_department(dept_id, active_only=True) → QuerySet
get_students_by_program(prog_id, active_only=True) → QuerySet
get_students_by_year_and_semester(year, sem, dept_id=None, prog_id=None) → QuerySet

get_active_students(department_id=None) → QuerySet
count_students_by_status(department_id=None) → Dict
```

### AcademicProgressSelector

```python
get_student_progress(student_id) → QuerySet
get_latest_progress(student_id) → AcademicProgress
get_progress_by_period(student_id, year, study_year, semester) → AcademicProgress
get_students_on_probation(department_id=None) → QuerySet
```

### StudentEnrollmentSelector

```python
get_student_enrollments(student_id) → QuerySet
get_active_enrollment(student_id) → StudentEnrollment
get_current_period_enrollment(student_id, year, semester) → StudentEnrollment
get_curriculum_enrollments(curriculum_id) → QuerySet
get_enrollments_by_status(student_id, status) → QuerySet
```

**Key Feature**: All selectors use `select_related()` and `prefetch_related()` to prevent N+1 queries.

## API Endpoints

### Student Management

```
POST   /api/students/                    # Create student
GET    /api/students/                    # List students (with filters)
GET    /api/students/{id}/               # Retrieve student
PUT    /api/students/{id}/               # Update student
PATCH  /api/students/{id}/               # Partial update
DELETE /api/students/{id}/               # Delete student (if allowed)

# Student-specific
GET    /api/students/me/                 # Own profile
GET    /api/students/{id}/academic-progress/   # Progress history
GET    /api/students/{id}/enrollments/   # Enrollment history
GET    /api/students/{id}/curriculum-units/    # Required units
GET    /api/students/{id}/timetable/     # Timetable (placeholder)
GET    /api/students/statistics/         # Student counts by status
```

### Profile Management

```
PUT    /api/profile/me/update/           # Update own limited fields
GET    /api/profile/me/update/           # View own profile
```

### Academic Progress

```
GET    /api/academic-progress/           # List all (admin only)
GET    /api/academic-progress/{id}/      # View specific record
```

### Enrollments

```
GET    /api/enrollments/                 # List enrollments
POST   /api/enrollments/{id}/withdraw/   # Withdraw enrollment
```

## Permissions

### Role-Based Access

| Action | Student | Lecturer | Dept Admin | Registrar | Super Admin |
|--------|---------|----------|-----------|-----------|------------|
| View own profile | ✅ | - | - | - | - |
| View dept students | - | - | ✅ | ✅ | ✅ |
| View all students | - | - | - | ✅ | ✅ |
| Create student | - | - | ✅ | ✅ | ✅ |
| Update student | - | - | ✅* | ✅ | ✅ |
| Delete student | - | - | - | ✅ | ✅ |
| Manage enrollments | - | - | ✅* | ✅ | ✅ |
| View progress | Students own | - | Dept's | ✅ | ✅ |

\* = Only for department members

### Permission Classes

```python
IsStudentOwnerOrAdmin          # Student views own or admin views any
CanManageStudents              # CUD operations
CanViewStudentProfile          # Read access
CanUpdateOwnProfile            # Students update own limited fields
CanViewAcademicProgress        # View progress
CanManageEnrollments           # Manage enrollments
IsDepartmentAdminOrSuper       # Department-restricted
```

## Validators

### StudentValidator

```python
validate_registration_number_unique(reg_num, exclude_id=None)
validate_email_unique(email, exclude_id=None)
validate_admission_year(year)
validate_study_year(year, program=None)
validate_semester(sem)
validate_phone_number(phone)
validate_gender(gender)
validate_enrollment_type(type)
validate_academic_status(status)
validate_department_program_match(dept, prog)
validate_student_can_update_profile(student)
validate_student_can_enroll(student)
```

### AcademicProgressValidator

```python
validate_gpa_range(gpa)           # 0.00-4.00
validate_cgpa_range(cgpa)         # 0.00-4.00
validate_credits_non_negative(credits)
validate_unique_period(student, year, study_year, sem)
```

### StudentEnrollmentValidator

```python
validate_curriculum_program_match(student, curriculum)
validate_curriculum_year_match(curriculum, study_year)
validate_curriculum_semester_match(curriculum, semester)
validate_student_can_withdraw(enrollment)
```

## Serializers

### StudentListSerializer
Lightweight for list endpoints - includes key fields only

### StudentDetailSerializer
Full details including related objects - for retrieve views

### StudentCreateUpdateSerializer
Accepts user_id, department_id, program_id - validates data

### StudentProfileUpdateSerializer
Limited fields for student self-update only

### StudentMyProfileSerializer
Student viewing own complete profile

## Validation Flow

```
Request Data
    ↓
Serializer validate_*() methods
    ↓
Validator.validate_*() methods
    ↓
Model clean() method
    ↓
Model save() calls full_clean()
    ↓
Database constraints
```

## Query Optimization Strategy

### N+1 Prevention

All selectors use optimal queries:

```python
# ❌ BAD - N+1 queries
students = Student.objects.all()
for student in students:
    curriculum = student.get_current_curriculum()  # Query per student!

# ✅ GOOD - Single optimized query
from apps.students.selectors import StudentSelector
students = StudentSelector.get_student_list()
# Already includes select_related and prefetch_related
```

### Indexing Strategy

```python
# High-traffic queries
- registration_number (unique)
- email (unique)
- status + is_active (filter queries)
- department + program (filtering)
- admission_year (reporting)
- study_year + semester (curricular queries)
```

## Deployment Readiness

### Database Considerations

1. **Migrations**: All models use Django migrations
2. **Constraints**: Database-level constraints for data integrity
3. **Indexes**: Strategic indexes for performance
4. **Scalability**: Ready for PostgreSQL with partitioning if needed

### Security

1. **Authentication**: JWT token-based (via Django REST Framework)
2. **Authorization**: Role-based permissions
3. **Validation**: World-class validation at multiple levels
4. **Data Protection**: Sensitive fields (email, phone) indexed safely

### Performance

1. **Query Optimization**: All selectors use select_related/prefetch_related
2. **Caching**: Ready for Redis caching layer
3. **Pagination**: Built into viewsets
4. **Filtering**: DjangoFilterBackend support

## Future Integration Points

### 1. Timetable Module
```
StudentTimetableService.prepare_student_timetable_context()
→ Returns optimized data for timetable generation
```

### 2. Curriculum Module
```
StudentCurriculumService.get_student_curriculum_units()
→ Fetches units for enrolled curriculum
```

### 3. Analytics Module
```
StudentAnalyticsService.get_student_statistics()
→ Provides student data for analytics
```

### 4. Notification Module
```
Student signals can trigger notifications on:
- Status changes
- Enrollment updates
- Progress milestones
```

## Error Handling

### HTTP Status Codes

- `200 OK`: Successful GET/PUT/PATCH
- `201 Created`: Successful POST
- `204 No Content`: Successful DELETE
- `400 Bad Request`: Validation error
- `401 Unauthorized`: No authentication
- `403 Forbidden`: No permission
- `404 Not Found`: Resource not found
- `500 Server Error`: Internal error

### Error Response Format

```json
{
    "error": "Descriptive error message",
    "field": ["Specific field error details"]
}
```

## Testing Strategy

### Unit Tests
- Model validation
- Service methods
- Validator functions

### Integration Tests
- API endpoints
- Permission checks
- Database operations

### Performance Tests
- Query counts
- Response times
- Load testing

## Configuration

### Settings Required

```python
# settings.py

INSTALLED_APPS = [
    'apps.students',
    # ... rest of apps
]

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Image upload settings
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Translations
USE_I18N = True
LANGUAGE_CODE = 'en-us'
```

## Migration Order

1. **Create users** (accounts app)
2. **Create departments** (departments app)
3. **Create programs** (programs app)
4. **Create students** (this module)
5. **Create curriculum** (curriculum app)
6. **Create curriculum units** (curriculum app)
7. **Create enrollments** (this module)

## Next Steps

1. **Run migrations**:
   ```bash
   python manage.py makemigrations students
   python manage.py migrate students
   ```

2. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

3. **Test endpoints**:
   ```bash
   python manage.py test apps.students
   ```

4. **Start development server**:
   ```bash
   python manage.py runserver
   ```

5. **Access admin**:
   Visit `http://localhost:8000/admin/`
