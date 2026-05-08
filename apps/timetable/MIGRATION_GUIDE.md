# Timetable System - Migration & Setup Guide

## Database Migration Guide

### Step 1: Create Initial Migrations (if not already created)

The timetable models should already exist. If migrations haven't been created:

```bash
# Create migrations for timetable app
python manage.py makemigrations timetable

# Review migration file at:
# apps/timetable/migrations/000X_initial.py
```

### Step 2: Apply Migrations

```bash
# Apply all pending migrations
python manage.py migrate

# Or apply specific app migrations
python manage.py migrate timetable

# Verify migrations
python manage.py showmigrations timetable
```

### Step 3: Check Database Schema

```bash
# View database schema for timetable models
python manage.py sqlmigrate timetable 0001

# Connect to PostgreSQL and verify tables
psql -U postgres -d your_database
\dt *timetable*
```

---

## Initial Data Setup

### 1. Create Academic Terms

Required before uploading timetable data:

```bash
# Via Django shell
python manage.py shell
```

```python
from apps.timetable.models import AcademicTerm
from datetime import date

# Create 2023-2024 Academic Year
AcademicTerm.objects.create(
    academic_year="2023-2024",
    semester=1,
    start_date=date(2023, 9, 1),
    end_date=date(2023, 12, 20),
    is_current=True
)

AcademicTerm.objects.create(
    academic_year="2023-2024",
    semester=2,
    start_date=date(2024, 1, 15),
    end_date=date(2024, 4, 30),
    is_current=False
)

# Verify creation
AcademicTerm.objects.all()
```

### 2. Import Programs

Before uploading, ensure programs exist:

```bash
# Programs should be created via the programs app
# Or via Django admin: http://localhost:8000/admin/programs/program/
```

```python
from apps.programs.models import Program

# Example: Create a program if doesn't exist
program, created = Program.objects.get_or_create(
    code="CS001",
    defaults={
        "name": "Computer Science",
        "description": "Bachelor of Science in Computer Science",
        "duration_years": 4,
    }
)
```

### 3. Create Rooms

Venues/locations must exist:

```python
from apps.rooms.models import Room

# Create rooms
rooms_data = [
    {"code": "A101", "name": "Lecture Hall A101", "capacity": 100},
    {"code": "A102", "name": "Lecture Hall A102", "capacity": 80},
    {"code": "B102", "name": "Lab B102", "capacity": 40},
]

for room in rooms_data:
    Room.objects.get_or_create(code=room["code"], defaults=room)
```

### 4. Create Lecturers

Lecturers must exist with university IDs:

```python
from apps.lecturers.models import Lecturer
from apps.accounts.models import User
from django.contrib.auth.models import Group

# Create user first
user = User.objects.create_user(
    email="john.smith@university.edu",
    first_name="John",
    last_name="Smith",
    university_id="LEC001",
    is_staff=False
)

# Create lecturer
lecturer = Lecturer.objects.create(
    user=user,
    department="Computer Science"
)
```

### 5. Create Curriculum Units

Program > Curriculum > CurriculumUnit hierarchy:

```python
from apps.curriculum.models import Program, Curriculum, CurriculumUnit, Unit

# Get or create program
program = Program.objects.get(code="CS001")

# Get or create curriculum
curriculum, _ = Curriculum.objects.get_or_create(
    program=program,
    defaults={"name": "CS Year 1 Semester 1"}
)

# Get or create unit
unit, _ = Unit.objects.get_or_create(
    code="COMP101",
    defaults={"name": "Introduction to Programming"}
)

# Create curriculum unit
curr_unit, _ = CurriculumUnit.objects.get_or_create(
    unit=unit,
    curriculum=curriculum,
    year_of_study=1,
    semester=1,
)
```

---

## Verification Checklist

Before uploading timetable data, verify:

```bash
python manage.py shell
```

```python
from apps.timetable.models import AcademicTerm
from apps.programs.models import Program
from apps.rooms.models import Room
from apps.lecturers.models import Lecturer
from apps.curriculum.models import CurriculumUnit

# 1. Academic Terms exist
print(f"Academic Terms: {AcademicTerm.objects.count()}")
for term in AcademicTerm.objects.all():
    print(f"  - {term.academic_year} S{term.semester}")

# 2. Programs exist
print(f"\nPrograms: {Program.objects.count()}")
print(f"  - {[p.code for p in Program.objects.all()]}")

# 3. Rooms exist
print(f"\nRooms: {Room.objects.count()}")
print(f"  - {[r.code for r in Room.objects.all()]}")

# 4. Lecturers exist
print(f"\nLecturers: {Lecturer.objects.count()}")
for lecturer in Lecturer.objects.select_related('user').all()[:5]:
    print(f"  - {lecturer.user.university_id}: {lecturer.user.get_full_name()}")

# 5. Curriculum Units exist
print(f"\nCurriculum Units: {CurriculumUnit.objects.count()}")
for cu in CurriculumUnit.objects.select_related('unit', 'curriculum__program')[:5]:
    print(f"  - {cu.curriculum.program.code}/{cu.unit.code}")

# 6. Exit
exit()
```

---

## Common Migration Issues & Solutions

### Issue: "No such table: timetable_xxx"

**Cause**: Migrations not applied

**Solution**:
```bash
python manage.py migrate
python manage.py migrate timetable
```

### Issue: "Foreign key constraint failed"

**Cause**: Required related model doesn't exist

**Solution**:
1. Verify all related objects exist (programs, rooms, lecturers, etc.)
2. Create missing objects via Django shell or admin
3. Check upload data references correct IDs/codes

### Issue: "Invalid day_of_week value"

**Cause**: Day abbreviation not in [mon, tue, wed, thu, fri, sat]

**Solution**:
1. Review Excel file for day names
2. Ensure only valid abbreviations are used
3. Check for extra spaces or case issues

### Issue: "Duplicate key value violates unique constraint"

**Cause**: Duplicate timetable sessions

**Solution**:
1. Check Excel file for duplicate rows
2. Remove duplicates from Excel
3. Or re-upload to same batch (will skip duplicates)

### Issue: "No matching query exists for model Course"

**Cause**: Program/Unit code doesn't match database

**Solution**:
1. Verify program codes in Excel exactly match database
2. Create missing programs/units
3. Check Excel: `PROGRAM_CODE/UNIT_CODE` format matches

---

## Database Optimization

### Create Indexes

```bash
python manage.py shell
```

```python
from django.db import connection

# Execute raw SQL to create indexes if not on deployment
indexes = [
    """CREATE INDEX IF NOT EXISTS idx_timetableuploadbatch_status 
       ON timetable_timetableuploadbatch(status);""",
    
    """CREATE INDEX IF NOT EXISTS idx_timetableslot_term_day 
       ON timetable_timetableslot(term_id, day_of_week);""",
    
    """CREATE INDEX IF NOT EXISTS idx_timetableslot_room_time 
       ON timetable_timetableslot(room_id, day_of_week, start_time);""",
    
    """CREATE INDEX IF NOT EXISTS idx_timetableslot_lecturer 
       ON timetable_timetableslot(lecturer_id, day_of_week);""",
    
    """CREATE INDEX IF NOT EXISTS idx_timetableconflict_type 
       ON timetable_timetableconflict(conflict_type, term_id);""",
]

with connection.cursor() as cursor:
    for index_sql in indexes:
        cursor.execute(index_sql)
        print(f"Created index: {index_sql.split('.')[1].split('(')[0]}")
```

### Enable Query Caching

In `settings.py`:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'redis_client.DefaultClient'
        }
    }
}

# Cache timetable queries for 1 hour
TIMETABLE_CACHE_TIMEOUT = 3600
```

---

## Backup & Recovery

### Backup Database

```bash
# Backup specific timetable tables
pg_dump -U postgres -d your_database \
  -t timetable_academicterm \
  -t timetable_timetableuploadbatch \
  -t timetable_timetableslot \
  -t timetable_timetableconflict \
  > timetable_backup.sql

# Or backup entire database
pg_dump -U postgres -d your_database > full_backup.sql

# Backup uploaded files
tar -czf timetable_uploads_backup.tar.gz media/timetable_uploads/
```

### Restore Database

```bash
# Restore from backup
psql -U postgres -d your_database < timetable_backup.sql

# Or restore entire database
psql -U postgres -d your_database < full_backup.sql
```

### Delete Timetable Data

```bash
python manage.py shell
```

```python
from apps.timetable.models import (
    TimetableUploadBatch,
    TimetableSlot,
    TimetableConflict,
)

# Delete all conflicts first (they reference slots)
TimetableConflict.objects.all().delete()

# Delete all slots
TimetableSlot.objects.all().delete()

# Delete upload batches
TimetableUploadBatch.objects.all().delete()

print("Timetable data deleted")
```

---

## Deployment Checklist

- [ ] All migrations applied: `python manage.py migrate`
- [ ] Academic terms created for relevant years
- [ ] Programs, rooms, lecturers created
- [ ] Database indexes created for performance
- [ ] Permissions configured in Django admin
- [ ] Static files collected: `python manage.py collectstatic`
- [ ] Test file upload in staging environment
- [ ] Review logs for any errors: `tail -f logs/timetable.log`
- [ ] Setup automated backups
- [ ] Configure logging to external service (Sentry, etc.)
- [ ] Document custom settings in production

---

## Environment Variables

Add to `.env` or `settings.py`:

```python
# Timetable Configuration
TIMETABLE_UPLOAD_MAX_SIZE = 10 * 1024 * 1024  # 10MB
TIMETABLE_UPLOAD_LOCATION = "timetable_uploads/%Y/%m/%d"
TIMETABLE_BATCH_SIZE = 100
TIMETABLE_CONFLICT_DETECTION_ENABLED = True
TIMETABLE_CACHE_DURATION = 3600  # 1 hour

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'timetable_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/timetable.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
        },
    },
    'loggers': {
        'timetable': {
            'handlers': ['timetable_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

---

## Support & Troubleshooting

For issues:

1. **Check Logs**: `tail -f logs/timetable.log`
2. **Django Debug Toolbar**: Enable in development
3. **Database Logs**: Check PostgreSQL slow query logs
4. **API Response**: Review error codes in response body
5. **Admin Interface**: Verify data in Django admin
6. **Load Test**: Use `locust` for load testing

```bash
# Install locust
pip install locust

# Run load test
locust -f loadtest.py --host=http://localhost:8000
```
