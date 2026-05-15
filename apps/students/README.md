# Students Module - README

## Overview

The Students Management Module is a production-level Django REST Framework application for managing student profiles, academic progress, and enrollments in the SMARTTT university system.

## Features

✅ Complete student profile management  
✅ Academic progress tracking  
✅ Curriculum-based unit assignment  
✅ Student enrollments management  
✅ Role-based access control (RBAC)  
✅ JWT authentication  
✅ Advanced filtering and search  
✅ Query optimization (no N+1 queries)  
✅ Comprehensive validation  
✅ Django admin integration  
✅ Pagination support  
✅ Production-ready error handling  

## Requirements

- Python 3.8+
- Django 4.0+
- Django REST Framework
- PostgreSQL
- django-filter
- djangorestframework-simplejwt
- Pillow (for image uploads)

## Installation

### 1. Clone and Setup

```bash
git clone <repository>
cd SMARTTT_BACKEND
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Database

```bash
# In settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'smarttt_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

### 5. Run Server

```bash
python manage.py runserver
```

### 6. Access Admin Interface

```
http://localhost:8000/admin/
```

## Quick Start

### Create a Student

The backend exposes both `POST /api/v1/auth/token/` for SimpleJWT and `POST /api/v1/accounts/auth/login/` for the custom accounts login flow. Use the one your frontend expects.

```bash
# Get JWT token
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Create student
curl -X POST http://localhost:8000/api/students/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "registration_number": "STU2024001",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "department_id": "550e8400-e29b-41d4-a716-446655440001",
    "program_id": "550e8400-e29b-41d4-a716-446655440002",
    "admission_year": 2024
  }'
```

### Get Student Profile

```bash
curl -X GET http://localhost:8000/api/students/550e8400-e29b-41d4-a716-446655440000/ \
  -H "Authorization: Bearer <token>"
```

### View Own Profile

```bash
curl -X GET http://localhost:8000/api/students/me/ \
  -H "Authorization: Bearer <student_token>"
```

## Module Structure

```
apps/students/
├── models/                    # Data models
│   ├── __init__.py
│   └── student.py            # Student, AcademicProgress, StudentEnrollment
│
├── serializers/              # API serializers
│   ├── __init__.py
│   ├── serializers.py        # All serializer classes
│   └── student_serializer.py
│
├── views/                    # API views/viewsets
│   ├── __init__.py
│   ├── views.py              # Main viewsets
│   └── student_viewset.py
│
├── services/                 # Business logic
│   └── __init__.py           # Service classes
│
├── selectors/                # Database queries
│   └── __init__.py           # Selector functions
│
├── validators/               # Validation logic
│   ├── __init__.py
│   └── student_validator.py
│
├── permissions/              # Access control
│   ├── __init__.py
│   └── permissions.py
│
├── utils/                    # Helper functions
│   └── __init__.py
│
├── urls.py                   # URL routing
├── admin.py                  # Django admin
├── apps.py                   # App configuration
├── ARCHITECTURE.md           # Architecture documentation
├── API_DOCUMENTATION.md      # API endpoints
├── MIGRATION_GUIDE.md        # Migration instructions
└── README.md                 # This file
```

## Configuration

### Settings (settings.py)

```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'rest_framework',
    'django_filters',
    'corsheaders',
    'apps.accounts',
    'apps.departments',
    'apps.programs',
    'apps.students',  # Add this
    # ... other apps
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

# Image uploads
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Translations
USE_I18N = True
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
```

### URL Configuration (urls.py)

```python
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api/', include('apps.students.urls')),
    # ... other paths
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## API Endpoints

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete endpoint documentation.

### Main Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/students/` | List students |
| POST | `/api/students/` | Create student |
| GET | `/api/students/{id}/` | Get student |
| PUT | `/api/students/{id}/` | Update student |
| PATCH | `/api/students/{id}/` | Partial update |
| DELETE | `/api/students/{id}/` | Delete student |
| GET | `/api/students/me/` | Own profile |
| GET | `/api/students/{id}/academic-progress/` | Progress history |
| GET | `/api/students/{id}/enrollments/` | Enrollment history |
| GET | `/api/students/{id}/curriculum-units/` | Required units |
| GET | `/api/students/{id}/timetable/` | Personalized timetable |

## Permissions

### Student Roles

- **Student**: View own profile, can't modify critical fields
- **Department Admin**: Manage students in their department
- **Registrar**: Full access to students
- **Super Admin**: Full access to everything

See [ARCHITECTURE.md](ARCHITECTURE.md#permissions) for detailed permission matrix.

## Data Validation

### Email & Registration Number

- Must be unique globally
- Email validated against Django's EmailField
- Registration number follows format: alphanumeric + hyphens

### Study Year & Semester

- Study year: 1-based, cannot exceed program duration
- Semester: Must be 1 or 2
- Admin must enforce consistency

### Academic Status

Valid values:
- `active`: Currently enrolled
- `inactive`: Not currently studying
- `suspended`: Temporarily suspended
- `graduated`: Completed program
- `withdrawn`: Left program
- `on_leave`: On approved leave

## Testing

### Run Tests

```bash
# All tests
python manage.py test apps.students

# Specific test class
python manage.py test apps.students.tests.StudentModelTests

# With coverage
coverage run --source='apps.students' manage.py test apps.students
coverage report
```

### Test Coverage

Use pytest and pytest-cov:

```bash
pip install pytest pytest-cov pytest-django
pytest apps/students/ --cov=apps/students --cov-report=html
```

## Performance

### Query Optimization

All selectors use `select_related()` and `prefetch_related()` to prevent N+1 queries:

```python
# Good - optimized query
from apps.students.selectors import StudentSelector
students = StudentSelector.get_student_list()

# Bad - N+1 queries
students = Student.objects.all()
for student in students:
    department = student.department  # Query per student!
```

### Database Indexes

Automatically created for:
- `registration_number`
- `email`
- `department + program`
- `academic_status + is_active`
- `admission_year`
- `study_year + semester`

### Caching (Future)

Planned caching layer:

```python
from django.views.decorators.cache import cache_page

@cache_page(60)  # Cache for 60 seconds
def get_student_list(request):
    ...
```

## Admin Dashboard

Access at `/admin/` after creating superuser.

### Features

- List/filter students by status, department, program
- Inline editing
- Bulk actions (activate/suspend/deactivate)
- Search by registration number, name, email
- View academic progress
- Manage enrollments

### Bulk Actions

- Mark students as active
- Mark students as inactive
- Suspend students
- Activate students

## File Uploads

### Profile Photo

- Supported formats: JPG, JPEG, PNG, GIF
- Max size: Configured in Django
- Stored in: `media/students/photos/{year}/{month}/`

Upload via API:

```bash
curl -X PATCH http://localhost:8000/api/profile/me/update/ \
  -H "Authorization: Bearer <token>" \
  -F "profile_photo=@photo.jpg"
```

## Error Handling

### HTTP Status Codes

- `200 OK`: Successful read
- `201 Created`: Successful creation
- `204 No Content`: Successful deletion
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found

### Error Response Format

```json
{
  "field_name": ["Error message"],
  "error": "General error message"
}
```

## Troubleshooting

### Common Issues

**Problem**: `User profile doesn't exist`
```bash
# Solution: Ensure user exists and has role='student'
```

**Problem**: `Department program mismatch`
```bash
# Solution: Ensure program.department matches department_id
```

**Problem**: `Study year exceeds program duration`
```bash
# Solution: Verify program duration_years matches student's year
```

### Debug Mode

Enable detailed logging:

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'apps.students': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Deployment

### Production Checklist

- [ ] Set `DEBUG = False`
- [ ] Set strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use PostgreSQL (not SQLite)
- [ ] Set up static/media file serving
- [ ] Configure CORS properly
- [ ] Set up SSL/TLS
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Run migrations
- [ ] Create backups

### Deployment via Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "config.wsgi:application"]
```

### Docker Compose

```yaml
version: '3'
services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: smarttt_db
      POSTGRES_PASSWORD: password

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
```

## Contributing

1. Fork repository
2. Create feature branch
3. Make changes
4. Write tests
5. Submit pull request

## License

Licensed under the MIT License

## Support

For documentation:
- [Architecture](ARCHITECTURE.md)
- [API Documentation](API_DOCUMENTATION.md)
- [Migration Guide](MIGRATION_GUIDE.md)

For issues or questions, contact the development team.

## Changelog

### v1.0.0 (Initial Release)

- Complete student profile management
- Academic progress tracking
- Student enrollments
- Role-based permissions
- Django admin integration
- JWT authentication
- Comprehensive API documentation
