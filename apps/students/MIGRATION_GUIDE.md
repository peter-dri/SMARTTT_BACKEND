# Students Module - Migration & Setup Guide

## Phase 1: Pre-Migration Planning

### 1. Data Audit

Before migration, document:

```bash
# Existing student records
SELECT COUNT(*) FROM existing_student_table;

# Active students
SELECT COUNT(*) FROM existing_student_table WHERE status = 'active';

# By program
SELECT program_id, COUNT(*) FROM existing_student_table GROUP BY program_id;
```

### 2. User Accounts Preparation

Ensure all users exist in `accounts_user` table:

```python
from apps.accounts.models import User

# Check existing students
existing_students = User.objects.filter(role='student')
print(f"Total student accounts: {existing_students.count()}")
```

### 3. Department/Program Validation

```python
from apps.departments.models import Department
from apps.programs.models import Program

# Verify departments
departments = Department.objects.all()
print(f"Total departments: {departments.count()}")

# Verify programs
programs = Program.objects.all()
print(f"Total programs: {programs.count()}")

# Check for orphaned programs
orphaned = Program.objects.filter(department__isnull=True)
if orphaned.exists():
    print(f"WARNING: {orphaned.count()} programs have no department!")
```

---

## Phase 2: Database Setup

### 1. Create Migrations

```bash
# If starting fresh (no migrations yet)
python manage.py makemigrations students

# Review generated migration
cat apps/students/migrations/0001_initial.py

# Create migration
python manage.py makemigrations --check
```

### 2. Review Migration

The migration will create:

```sql
CREATE TABLE students_student (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL UNIQUE,
    registration_number VARCHAR(50) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    gender VARCHAR(20) DEFAULT 'prefer_not_to_say',
    email VARCHAR(254) NOT NULL UNIQUE,
    phone_number VARCHAR(20),
    date_of_birth DATE,
    faculty_id UUID,
    department_id UUID NOT NULL,
    program_id UUID NOT NULL,
    current_study_year SMALLINT DEFAULT 1,
    current_semester SMALLINT DEFAULT 1,
    admission_year INTEGER NOT NULL,
    academic_status VARCHAR(20) DEFAULT 'active',
    enrollment_type VARCHAR(20) DEFAULT 'full_time',
    is_active BOOLEAN DEFAULT TRUE,
    profile_photo VARCHAR(100),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES accounts_user(id),
    FOREIGN KEY (faculty_id) REFERENCES departments_department(id),
    FOREIGN KEY (department_id) REFERENCES departments_department(id),
    FOREIGN KEY (program_id) REFERENCES programs_program(id),
    
    CONSTRAINT uq_student_registration_number UNIQUE (registration_number),
    CONSTRAINT uq_student_email UNIQUE (email),
    CONSTRAINT ck_study_year_positive CHECK (current_study_year >= 1),
    CONSTRAINT ck_semester_positive CHECK (current_semester >= 1),
    CONSTRAINT ck_admission_year_valid CHECK (admission_year >= 1900)
);

CREATE INDEX idx_student_registration ON students_student(registration_number);
CREATE INDEX idx_student_email ON students_student(email);
CREATE INDEX idx_student_dept_prog ON students_student(department_id, program_id);
CREATE INDEX idx_student_status_active ON students_student(academic_status, is_active);
```

### 3. Apply Migrations

```bash
# Dry run first
python manage.py migrate --plan students

# Apply migrations
python manage.py migrate students

# Verify
python manage.py showmigrations students
```

---

## Phase 3: Data Migration (From Legacy System)

### 1. Create Data Migration Script

```python
# apps/students/migrations/0002_load_legacy_students.py

from django.db import migrations
from django.utils import timezone
import os

def load_legacy_students(apps, schema_editor):
    """
    Load students from legacy system.
    
    This assumes legacy data is available via connection string.
    """
    Student = apps.get_model('students', 'Student')
    User = apps.get_model('accounts', 'User')
    Department = apps.get_model('departments', 'Department')
    Program = apps.get_model('programs', 'Program')
    
    # Example: Load from CSV
    import csv
    
    csv_file = os.path.join(os.path.dirname(__file__), 'legacy_students.csv')
    
    if not os.path.exists(csv_file):
        print(f"Warning: Legacy data file {csv_file} not found. Skipping migration.")
        return
    
    migrated_count = 0
    error_count = 0
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                # Get related objects
                user = User.objects.get(university_id=row['university_id'])
                department = Department.objects.get(code=row['department_code'])
                program = Program.objects.get(code=row['program_code'])
                
                # Create student
                student, created = Student.objects.get_or_create(
                    registration_number=row['registration_number'],
                    defaults={
                        'user': user,
                        'first_name': row['first_name'],
                        'last_name': row['last_name'],
                        'email': row['email'],
                        'phone_number': row.get('phone_number', ''),
                        'gender': row.get('gender', 'prefer_not_to_say'),
                        'date_of_birth': row.get('date_of_birth'),
                        'department': department,
                        'program': program,
                        'admission_year': int(row['admission_year']),
                        'current_study_year': int(row.get('current_study_year', 1)),
                        'current_semester': int(row.get('current_semester', 1)),
                        'academic_status': row.get('academic_status', 'active').lower(),
                        'is_active': row.get('is_active', 'true').lower() == 'true',
                    }
                )
                
                if created:
                    migrated_count += 1
                    
            except (User.DoesNotExist, Department.DoesNotExist, Program.DoesNotExist) as e:
                error_count += 1
                print(f"Error loading student {row.get('registration_number')}: {e}")
            except Exception as e:
                error_count += 1
                print(f"Unexpected error: {e}")
    
    print(f"Migrated: {migrated_count} students")
    print(f"Errors: {error_count}")


def reverse_migration(apps, schema_editor):
    """Reverse the migration if needed."""
    Student = apps.get_model('students', 'Student')
    Student.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_legacy_students, reverse_migration),
    ]
```

### 2. Prepare Legacy Data CSV

Create `legacy_students.csv`:

```csv
registration_number,university_id,first_name,last_name,email,phone_number,gender,date_of_birth,department_code,program_code,admission_year,current_study_year,current_semester,academic_status,is_active
STU2024001,user-001,John,Doe,john@example.com,+1234567890,male,2002-01-15,CS,CS-BSC,2024,1,1,active,true
STU2024002,user-002,Jane,Smith,jane@example.com,+9876543210,female,2002-05-20,CS,CS-BSC,2024,1,1,active,true
```

### 3. Run Data Migration

```bash
# Create detailed migration (not automatically generated)
python manage.py datamigration students load_legacy_students --empty

# Edit the migration file with script above

# Run migration
python manage.py migrate students

# Verify
python manage.py shell
>>> from apps.students.models import Student
>>> Student.objects.count()
>>> Student.objects.first().__dict__
```

---

## Phase 4: Validation & Testing

### 1. Data Validation

```python
from apps.students.models import Student
from django.core.exceptions import ValidationError

# Check for missing data
print("Validation checks:")

# Missing users
orphaned_students = [s for s in Student.objects.all() if s.user is None]
print(f"Orphaned students: {len(orphaned_students)}")

# Duplicate emails
from django.db.models import Count
duplicates = Student.objects.values('email').annotate(count=Count('email')).filter(count__gt=1)
print(f"Duplicate emails: {duplicates.count()}")

# Invalid study years
invalid_years = Student.objects.filter(current_study_year__lt=1)
print(f"Invalid study years: {invalid_years.count()}")

# Study year exceeds program duration
for student in Student.objects.all():
    if student.current_study_year > student.program.duration_years:
        print(f"Warning: {student.registration_number} exceeds program duration")

# Run full_clean on sample
sample = Student.objects.first()
if sample:
    try:
        sample.full_clean()
        print("Sample student valid ✓")
    except ValidationError as e:
        print(f"Sample student invalid: {e}")
```

### 2. Query Testing

```python
from apps.students.selectors import StudentSelector

# Test selector queries
students = StudentSelector.get_student_list()
print(f"Total students: {students.count()}")

# Test by department
dept_students = StudentSelector.get_students_by_department(department_id='...')
print(f"Department students: {dept_students.count()}")

# Test active students
active = StudentSelector.get_active_students()
print(f"Active students: {active.count()}")

# Test by year/semester
year2_sem1 = StudentSelector.get_students_by_year_and_semester(2, 1)
print(f"Year 2, Semester 1: {year2_sem1.count()}")
```

### 3. API Testing

```bash
# Get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' | jq -r '.access')

# Test endpoints
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/students/

# Filter by department
curl -H "Authorization: Bearer $TOKEN" \
  'http://localhost:8000/api/students/?department__id=abc123'

# Search
curl -H "Authorization: Bearer $TOKEN" \
  'http://localhost:8000/api/students/?search=john'

# Statistics
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/students/statistics/
```

---

## Phase 5: Admin Configuration

### 1. Access Django Admin

```
http://localhost:8000/admin/
```

### 2. Manage Students

- View/edit students
- Filter by department, program, status
- Bulk actions: activate/suspend students
- View academic progress

### 3. Sample Admin Tasks

```python
# Programmatic admin operations
from apps.students.models import Student

# Suspend all inactive students
inactive = Student.objects.filter(is_active=False)
inactive.update(academic_status='suspended')
print(f"Suspended {inactive.count()} inactive students")

# Activate year 1 students
year1 = Student.objects.filter(current_study_year=1)
year1.update(is_active=True, academic_status='active')
print(f"Activated {year1.count()} year 1 students")
```

---

## Phase 6: Integration Setup

### 1. Link to Curriculum Module

```python
# Create sample enrollments
from apps.students.models import Student, StudentEnrollment
from apps.curriculum.models import Curriculum

student = Student.objects.first()
curriculum = student.get_current_curriculum()

if curriculum:
    enrollment = StudentEnrollment.objects.create(
        student=student,
        curriculum=curriculum,
        academic_year=student.academic_year_string,
        study_year=student.current_study_year,
        semester=student.current_semester,
        enrollment_status='enrolled'
    )
    print(f"Created enrollment: {enrollment}")
```

### 2. Link to Timetable Module

```python
# Prepare timetable context
from apps.students.services import StudentTimetableService

student = Student.objects.first()
timetable_context = StudentTimetableService.prepare_student_timetable_context(student)
print(timetable_context)
```

---

## Phase 7: Production Deployment

### 1. Pre-Deployment Checklist

- [ ] All migrations created and tested
- [ ] Data validated
- [ ] API endpoints tested
- [ ] Permissions verified
- [ ] Backup created
- [ ] Rollback plan in place
- [ ] Monitoring configured
- [ ] Logging enabled

### 2. Deployment Steps

```bash
# 1. Backup production database
pg_dump smarttt_db > smarttt_backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Pull code
git pull origin main

# 3. Update dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate students

# 5. Collect static files
python manage.py collectstatic --noinput

# 6. Warm up cache
python manage.py shell
>>> from apps.students.selectors import StudentSelector
>>> StudentSelector.get_student_list()  # Cache warm-up

# 7. Verify endpoints
curl http://localhost:8000/api/students/
```

### 3. Rollback Plan

```bash
# If issues occur:
python manage.py migrate students 0001_initial  # Rollback to previous migration
# Restore from backup if needed
psql smarttt_db < smarttt_backup.sql
```

---

## Phase 8: Monitoring & Maintenance

### 1. Monitor Queries

```python
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as context:
    from apps.students.selectors import StudentSelector
    students = StudentSelector.get_student_list()
    list(students)  # Force evaluation

print(f"Queries executed: {len(context.captured_queries)}")
for query in context.captured_queries:
    print(f"- {query['time']:.3f}s: {query['sql'][:100]}...")
```

### 2. Monitor Performance

```python
import time
from apps.students.selectors import StudentSelector

start = time.time()
students = StudentSelector.get_student_list()
count = students.count()
elapsed = time.time() - start

print(f"Query took {elapsed:.3f}s, found {count} students")
```

### 3. Regular Maintenance

```bash
# Weekly
python manage.py shell
>>> from django.core.management import call_command
>>> call_command('clearsessions')  # Clear expired sessions

# Monthly
python manage.py dbshell
=> ANALYZE;  # Update query planner statistics
=> REINDEX;  # Rebuild indexes if fragmented
```

---

## Troubleshooting

### Issue: Foreign Key Constraint Violation

```
IntegrityError: violates foreign key constraint
```

**Solution**: Ensure related objects exist:

```python
from apps.students.validators import StudentValidator

# Check all constraints before creating
user = User.objects.get(id=user_id)
department = Department.objects.get(id=dept_id)
program = Program.objects.get(id=prog_id)

StudentValidator.validate_department_program_match(department, program)
```

### Issue: Unique Constraint Violation

```
IntegrityError: duplicate key value violates unique constraint
```

**Solution**: Check for duplicates:

```python
from django.db.models import Count

# Find duplicate registration numbers
duplicates = Student.objects.values('registration_number')\
    .annotate(count=Count('id')).filter(count__gt=1)

for dup in duplicates:
    students = Student.objects.filter(registration_number=dup['registration_number'])
    print(f"Duplicate: {dup['registration_number']} - {students.count()} records")
    # Merge or delete as needed
```

### Issue: Null Values in Required Fields

**Solution**: Validate before migration:

```python
# Check for missing data
students_no_email = Student.objects.filter(email__isnull=True)
print(f"Students with no email: {students_no_email.count()}")

# Generate defaults if needed
for student in students_no_email:
    student.email = f"student_{student.id}@generated.local"
    student.save()
```

---

## Rollback Procedures

### Full Rollback

```bash
# 1. Stop application
systemctl stop smarttt-app  # or your service

# 2. Restore database backup
psql smarttt_db < smarttt_backup.sql

# 3. Rollback code
git checkout previous-commit

# 4. Restart application
systemctl start smarttt-app
```

### Partial Rollback (Keep Data)

```bash
# Revert last migration
python manage.py migrate students 0001_initial

# But keep student data if needed:
# (Data will be preserved, only schema reverts)
```

---

## Success Criteria

✅ All students migrated successfully  
✅ No orphaned records  
✅ All constraints validated  
✅ API endpoints responsive  
✅ Permissions working correctly  
✅ Admin interface accessible  
✅ Integrations working  
✅ Monitoring active  

---

## Support

For issues during migration:
1. Check logs: `tail -f logs/students.log`
2. Review validation: `python manage.py shell`
3. Contact development team

---

## Next Steps

After successful migration:

1. **Create Academic Progress Records**
   ```python
   # Load historical GPA data if available
   ```

2. **Link to Timetable Module**
   ```python
   # Configure timetable integration
   ```

3. **Set Up Notifications**
   ```python
   # Configure student status change notifications
   ```

4. **Configure Analytics**
   ```python
   # Set up reporting dashboards
   ```
