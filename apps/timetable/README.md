# Timetable Upload System

**Production-level timetable Excel upload and processing system** for the smart university backend.

## 🎯 Quick Start

### 1. Installation

```bash
# Ensure dependencies are installed
pip install django djangorestframework pandas openpyxl

# Apply migrations
python manage.py migrate

# Create superuser (if needed)
python manage.py createsuperuser
```

### 2. Create Initial Data

```bash
python manage.py shell
```

```python
from apps.timetable.models import AcademicTerm
from datetime import date

# Create academic term
AcademicTerm.objects.create(
    academic_year="2023-2024",
    semester=1,
    start_date=date(2023, 9, 1),
    end_date=date(2023, 12, 20),
    is_current=True
)

# Create programs, rooms, lecturers, etc.
# See MIGRATION_GUIDE.md for detailed setup
exit()
```

### 3. Upload Timetable

```bash
# Create Excel file with required columns (see File Format below)
# Then upload via API:

curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@timetable.xlsx" \
  http://localhost:8000/api/timetable/upload/
```

### 4. Check Results

```bash
# View upload history
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/timetable/uploads/

# View conflicts
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/timetable/conflicts/
```

---

## 📋 Excel File Format

### Required Columns

| Column | Type | Example | Notes |
|--------|------|---------|-------|
| `academic_year` | String | `2023-2024` | YYYY or YYYY-YYYY format |
| `semester` | Integer | `1` | 1, 2, or 3 |
| `program_code` | String | `CS001` | Must exist in database |
| `unit_code` | String | `COMP101` | Must exist with program |
| `year_of_study` | Integer | `1` | 1-10 |
| `day_of_week` | String | `mon` | mon, tue, wed, thu, fri, sat |
| `start_time` | Time | `09:00` | HH:MM or HH:MM:SS format |
| `end_time` | Time | `10:30` | Must be after start_time |
| `room_code` | String | `A101` | Must exist in database |
| `lecturer_university_id` | String | `LEC001` | Must exist in database |
| `class_group` | String | `MAIN` | Optional, defaults to MAIN |

### Sample Excel

```
academic_year | semester | program_code | unit_code | year_of_study | day_of_week | start_time | end_time | room_code | lecturer_university_id | class_group
2023-2024     | 1        | CS001        | COMP101   | 1             | mon         | 09:00      | 10:30    | A101      | LEC001               | MAIN
2023-2024     | 1        | CS001        | COMP102   | 1             | mon         | 11:00      | 12:30    | B102      | LEC002               | GROUP_A
```

---

## 📚 API Endpoints

### Upload Timetable
```
POST /api/timetable/upload/
- File: Excel file (.xlsx or .xls)
- Response: Upload report with status and errors
```

### List Uploads
```
GET /api/timetable/uploads/?status=processed&page=1
- Filters: status, uploaded_by
- Pagination: page, page_size
- Response: List of previous uploads
```

### Get Upload Details
```
GET /api/timetable/uploads/{id}/
- Response: Upload details with all created slots
```

### List Timetable Slots
```
GET /api/timetable/slots/?term=ID&day_of_week=mon
- Filters: term, day_of_week, room, lecturer, upload_batch
- Response: List of timetable sessions
```

### Get Slot Details
```
GET /api/timetable/slots/{id}/detailed/
- Response: Full slot info with related data
```

### List Conflicts
```
GET /api/timetable/conflicts/?conflict_type=room&term=ID
- Filters: conflict_type (room, lecturer, program), term
- Response: Detected timetable conflicts
```

---

## 🏗️ Architecture

### Layered Architecture

```
┌─────────────────────┐
│     API Layer       │ Views, Serializers, Routing
├─────────────────────┤
│   Service Layer     │ Business Logic, Pipeline
├─────────────────────┤
│  Validation Layer   │ Rules, Constraints
├─────────────────────┤
│   Utility Layer     │ Logging, Exceptions, Helpers
├─────────────────────┤
│   Database Layer    │ Models, ORM
└─────────────────────┘
```

### Key Services

- **TimetableUploadPipelineService** - Orchestrates upload workflow
- **TimetableExcelParserService** - Reads Excel files
- **TimetableTransformService** - Normalizes data
- **TimetablePersistenceService** - Saves to database
- **TimetableConflictDetectionService** - Finds conflicts

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed design documentation.

---

## 🔍 Error Handling

The system provides detailed error reporting at multiple levels:

### File Validation Errors
```json
{
  "status": "error",
  "error": {
    "code": "FILE_VALIDATION_ERROR",
    "message": "File validation failed",
    "details": ["File size exceeds 10MB limit"]
  }
}
```

### Data Validation Errors
```json
{
  "status": "partial",
  "summary": {
    "rows_received": 150,
    "rows_saved": 145,
    "rows_failed": 5
  },
  "errors": [
    "Row 5: Missing required field 'room_code'",
    "Row 12: Invalid semester value",
    "Row 23: Lecturer not found: LEC999"
  ]
}
```

---

## 🔐 Permissions

- **Admin/Staff**: Can upload files and manage timetable
- **Students/Lecturers**: Can view timetable slots (read-only)
- **Anonymous**: No access

All endpoints require authentication via Bearer token.

---

## 📊 Admin Interface

Access Django admin at `/admin/`:

- **Academic Terms**: Create and manage terms
- **Upload Batches**: View upload history and status
- **Timetable Slots**: Browse all sessions with filtering
- **Conflicts**: View and analyze detected conflicts

---

## 🔧 Settings

Add to `settings.py`:

```python
TIMETABLE = {
    'UPLOAD_MAX_SIZE': 10 * 1024 * 1024,  # 10MB
    'BATCH_SIZE': 100,  # Bulk operations batch size
    'CACHE_TIMEOUT': 3600,  # 1 hour
}
```

---

## 📝 Documentation

- **[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)** - Complete API reference with examples
- **[MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)** - Database setup and migration procedures
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System design and implementation details

---

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "Academic term not found" | Create term via admin or API first |
| "Lecturer not found" | Verify lecturer_university_id exists in database |
| "File validation failed" | Use .xlsx format, max 10MB |
| "Duplicate session" | Check Excel for duplicate rows |

See [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md#error-codes--troubleshooting) for more solutions.

---

## 📋 Features

✅ **Excel File Upload**
- Support for .xlsx and .xls formats
- Size validation (max 10MB)
- Safe error handling

✅ **Data Validation**
- Column structure validation
- Row-level data validation
- Type checking and conversion
- Duplicate detection

✅ **Data Processing**
- Automatic data transformation
- Reference lookups (terms, programs, rooms, lecturers)
- Transaction-safe database operations

✅ **Conflict Detection**
- Room double-booking detection
- Lecturer schedule conflicts
- Program schedule conflicts
- Detailed conflict reporting

✅ **Comprehensive Reporting**
- Upload status tracking
- Row-level error reporting
- Conflict statistics
- Success rate calculation

✅ **Audit Trail**
- Structured logging
- Upload history
- Error tracking
- User attribution

---

## 🚀 Performance

- **Optimized Queries**: select_related, prefetch_related
- **Bulk Operations**: Batch size configuration
- **Caching**: Configurable cache duration
- **Indexes**: Database-level optimization
- **Pagination**: Efficient large result handling

---

## 🔄 Workflow

1. **Upload** → Admin uploads Excel file
2. **Validate** → System validates structure and data
3. **Parse** → Extract rows and normalize data
4. **Transform** → Convert to database format
5. **Save** → Store in database with transaction safety
6. **Detect** → Find timetable conflicts
7. **Report** → Return detailed status report

---

## 🛠️ Development

### Running Tests

```bash
# Run all tests
python manage.py test apps.timetable

# Run specific test
python manage.py test apps.timetable.tests.TestUploadAPI

# Run with coverage
coverage run --source='apps.timetable' manage.py test
coverage report
```

### Code Quality

```bash
# Format code
black apps/timetable/

# Check style
flake8 apps/timetable/

# Type checking
mypy apps/timetable/
```

---

## 📦 Dependencies

- **Django** >= 3.2
- **Django REST Framework** >= 3.12
- **pandas** >= 1.3
- **openpyxl** >= 3.6

---

## 📄 License

Part of SMART University Backend Project

---

## 👥 Support

For issues or questions:
1. Check documentation files
2. Review error codes and solutions
3. Check Django logs
4. Contact system administrator

---

## 🎓 Learning Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [openpyxl Documentation](https://openpyxl.readthedocs.io/)

---

**Version**: 1.0.0
**Last Updated**: 2024-01-15
