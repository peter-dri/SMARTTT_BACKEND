# Timetable System - Architecture & Implementation Guide

## System Architecture

### Overview

The timetable upload system follows a **layered, modular architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                            │
│  (Views, Serializers, URL Routing, Error Handling)         │
└────────────┬────────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────────┐
│                      Service Layer                          │
│  (Business Logic, Pipeline Orchestration)                  │
│  - TimetableUploadPipelineService                          │
│  - TimetableExcelParserService                             │
│  - TimetableTransformService                               │
│  - TimetablePersistenceService                             │
│  - TimetableConflictDetectionService                       │
└────────────┬────────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────────┐
│                    Validation Layer                         │
│  (Data Validation, Rules Enforcement)                      │
│  - ExcelFileValidator                                      │
│  - TimetableUploadValidator                                │
│  - TimetableDataConsistencyValidator                       │
│  - ConflictValidationRules                                 │
└────────────┬────────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────────┐
│                    Utility Layer                            │
│  (Helpers, Logging, Constants, Error Handling)             │
│  - TimetableLogger                                         │
│  - TimetableResponseFormatter                              │
│  - Exceptions (ExcelParsingException, etc.)               │
│  - Constants (REQUIRED_COLUMNS, etc.)                      │
└────────────┬────────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────────┐
│                   Database Models                           │
│  (Persistence Layer)                                       │
│  - TimetableUploadBatch                                    │
│  - TimetableSlot                                           │
│  - TimetableConflict                                       │
│  - AcademicTerm                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. API Layer (`views/`, `serializers/`, `urls.py`)

**Responsibility**: HTTP request/response handling, authentication, authorization

**Components**:
- `TimetableUploadAPIView` - File upload endpoint
- `AcademicTermViewSet` - CRUD for academic terms
- `TimetableSlotViewSet` - Query and manage timetable slots
- `TimetableConflictViewSet` - List and filter conflicts
- `TimetableUploadListViewSet` - View upload history

**Key Features**:
- DRF permission classes (role-based access control)
- Request validation via serializers
- Pagination and filtering
- Detailed error responses

**Example**:
```python
# api/timetable/upload/
POST /api/timetable/upload/ with Excel file
→ TimetableUploadAPIView.post()
→ Returns upload report with status, row counts, errors
```

### 2. Service Layer (`services/`)

**Responsibility**: Business logic orchestration, data transformation

**Core Services**:

#### TimetableUploadPipelineService
Orchestrates complete upload workflow:
1. Parse Excel file
2. Validate structure
3. Extract and validate rows  
4. Transform data
5. Persist to database
6. Detect conflicts
7. Generate report

```python
pipeline = TimetableUploadPipelineService()
result = pipeline.execute(upload_batch)
# Returns: {"status": "success|partial|error", "summary": {...}, "errors": [...]}
```

#### TimetableExcelParserService
- Reads Excel files using pandas
- Normalizes column names
- Extracts data rows
- Handles missing cells and invalid formats

#### TimetableTransformService
- Type conversion and normalization
- Time parsing and validation
- Day abbreviation mapping
- Data consistency checks

#### TimetablePersistenceService
- Database model lookups with error handling
- Duplicate detection
- Transactional slot creation
- Detailed error reporting per row

#### TimetableConflictDetectionService
- Time overlap detection
- Multi-type conflict identification
- Conflict persistence with details
- Batch conflict reporting

### 3. Validation Layer (`validators/`)

**Responsibility**: Data validation rules and constraints

**Validators**:

```python
# File validation
ExcelFileValidator.validate_file_extension(filename)
ExcelFileValidator.validate_file_size(file_size)

# Data validation
TimetableUploadValidator.validate_columns(columns)
TimetableUploadValidator.validate_row(row, row_number)

# Consistency checks
TimetableDataConsistencyValidator.validate_no_duplicate_sessions(rows)

# Conflict rules
ConflictValidationRules.would_cause_lecturer_conflict(...)
ConflictValidationRules.would_cause_room_conflict(...)
```

### 4. Utility Layer (`utils/`)

**Responsibility**: Cross-cutting concerns, helpers

**Components**:

#### Exceptions (`utils/exceptions.py`)
- Custom exception classes with error codes
- Proper HTTP status codes
- Clear error messages

```python
# Examples
FileValidationException("Invalid file format")
ExcelParsingException("Cannot parse Excel file")
ResourceNotFoundException("Room not found: ABC123")
DuplicateSessionException("Duplicate session detected")
```

#### Response Formatter (`utils/response_formatter.py`)
- Consistent API response structure
- Status codes (success, partial, error)
- Detailed error information

```python
TimetableResponseFormatter.upload_response(
    upload_batch_id="...",
    rows_received=150,
    rows_saved=145,
    rows_failed=5,
    validation_errors=[...],
    conflicts_detected=3
)
```

#### Logger (`utils/logger.py`)
- Structured logging with JSON format
- Operation tracking
- Error documentation
- Conflict reporting

```python
TimetableLogger.log_upload_started(upload_batch_id, filename)
TimetableLogger.log_validation_error(upload_batch_id, row_number, field, error)
TimetableLogger.log_upload_completed(upload_batch_id, rows_received, rows_saved)
```

#### Constants (`utils/constants.py`)
- Configuration values
- Valid field values
- File constraints
- Database batch sizes

### 5. Database Models (`models/`)

**Core Models**:

```
AcademicTerm
├── academic_year (CharField)
├── semester (PositiveSmallIntegerField)
├── start_date, end_date (DateField)
└── is_current (BooleanField)

TimetableUploadBatch
├── uploaded_by (ForeignKey → User)
├── source_file (FileField)
├── status (RECEIVED|VALIDATED|FAILED|PROCESSED)
├── rows_received, rows_saved (PositiveIntegerField)
└── validation_errors (JSONField)

TimetableSlot
├── term (ForeignKey → AcademicTerm)
├── curriculum_unit (ForeignKey → CurriculumUnit)
├── lecturer (ForeignKey → Lecturer)
├── room (ForeignKey → Room)
├── day_of_week, start_time, end_time
├── class_group (CharField)
└── upload_batch (ForeignKey → TimetableUploadBatch)

TimetableConflict
├── conflict_type (ROOM|LECTURER|PROGRAM)
├── term (ForeignKey → AcademicTerm)
├── slot_a, slot_b (ForeignKey → TimetableSlot)
└── details (JSONField)
```

---

## Data Flow Diagram

### Upload Processing Pipeline

```
Excel File
    │
    ▼
┌─────────────────────┐
│ Parse Excel File    │
│ (pandas.read_excel) │
└──────────┬──────────┘
           │
           ▼
    ┌─────────────────┐
    │ Validate        │
    │ Columns Present │
    └──────┬──────────┘
           │
           ▼
    ┌──────────────────┐
    │ Extract Rows     │
    │ Normalize Data   │
    └──────┬───────────┘
           │
           ▼
    ┌────────────────────────┐
    │ Validate Each Row      │
    │ - Types               │
    │ - Ranges              │
    │ - Formats             │
    └──────┬─────────────────┘
           │
         Valid?─────No────┐
           │              │
         Yes              ▼
           │         Store Error
           │         Continue
           ▼
    ┌──────────────────┐      Not OK?──────No─┐
    │ Check for        │                      │
    │ Duplicates       │      Yes──────┐      │
    └──────┬───────────┘               │      │
           │                           │      │
           ▼                           ▼      │
        OK?──────No──────Show Error    │      │
           │                           │      │
         Yes                           │      │
           ▼                           │      │
    ┌──────────────────┐              │      │
    │ Transform Data   │              │      │
    │ Parse times      │◄─────────────┘      │
    │ Map fields       │                     │
    └──────┬───────────┘                     │
           │                                │
           ▼                                │
    ┌──────────────────────────┐            │
    │ Lookup References        │            │
    │ - Term                  │            │
    │ - Program/Unit          │            │
    │ - Room                  │            │
    │ - Lecturer              │            │
    └──────┬───────────────────┘            │
           │                               │
         Found?─────No────┐               │
           │              │               │
         Yes              ▼               │
           │         ResourceNotFound     │
           │         Error               │
           ▼                             │
    ┌──────────────────┐                │
    │ Save Slot to DB  │                │
    │ (Transaction)    │                │
    └──────┬───────────┘                │
           │                           │
         Success?────No──────┐        │
           │                 │        │
         Yes                 ▼        │
           ▼            DB Error      │
    ┌──────────────────┐             │
    │ Add to Saved     │             │
    │ Slots List       │             │
    └──────┬───────────┘             │
           │                        │
           ▼
    Continue with
    next row
           │
           ▼ (All rows processed)
    ┌──────────────────────┐
    │ Detect Conflicts     │
    │ - Room clashes      │
    │ - Lecturer overload │
    │ - Program conflicts │
    └──────┬───────────────┘
           │
           ▼
    ┌──────────────────┐
    │ Generate Report  │
    │ - Status        │
    │ - Row counts    │
    │ - Errors        │
    │ - Conflicts     │
    └──────┬───────────┘
           │
           ▼
      Return to API
```

---

## Error Handling Strategy

### Multi-Level Error Handling

```python
# Level 1: File Validation
try:
    ExcelFileValidator.validate_file_extension(filename)
    ExcelFileValidator.validate_file_size(file_size)
except FileValidationException as e:
    return 400 with error

# Level 2: Parsing
try:
    dataframe = parser.parse(file_path)
except ExcelParsingException as e:
    return 400 with error

# Level 3: Data Validation
for row in rows:
    is_valid, errors = TimetableUploadValidator.validate_row(row)
    if not is_valid:
        validation_errors.extend(errors)
        continue

# Level 4: Resource Lookup
try:
    term = AcademicTerm.objects.get(...)
except AcademicTerm.DoesNotExist:
    return ResourceNotFoundException

# Level 5: Database Operation
try:
    slot = TimetableSlot.objects.create(...)
except IntegrityError:
    return DatabaseOperationException

# Level 6: Conflict Detection
conflicts = conflict_service.detect(saved_slots)
```

### Error Response Format

```json
{
  "status": "error|partial|success",
  "error": {
    "code": "FILE_VALIDATION_ERROR",
    "message": "File validation failed",
    "details": ["File size exceeds 10MB"]
  }
}
```

---

## Implementation Best Practices

### 1. Service Layer Pattern
- Business logic separate from views
- Easy to test and reuse
- Clear dependency injection

```python
class MyView(APIView):
    def post(self, request):
        service = TimetableUploadPipelineService()
        result = service.execute(...)
        return Response(result)
```

### 2. Transaction Safety
- Use `@transaction.atomic` for multi-step operations
- Rollback on any failure
- Prevent partial update

```python
@transaction.atomic
def save_rows(self, upload_batch, rows):
    for row in rows:
        slot = TimetableSlot.objects.create(...)
    # Auto-rollback if exception occurs
```

### 3. Comprehensive Logging
- Log at all stages
- Include context (IDs, user, operation)
- Use structured format (JSON)

```python
self.logger.log_upload_started(upload_batch_id, filename)
self.logger.log_validation_error(upload_batch_id, row_number, field, error)
self.logger.log_upload_completed(upload_batch_id, rows_saved, conflicts_detected)
```

### 4. Error Recovery
- Continue processing on non-critical errors
- Collect all errors for reporting
- Mark batch status appropriately

```python
errors = []
for row in rows:
    try:
        process_row(row)
    except Exception as e:
        errors.append({"row": row_num, "error": str(e)})
        continue  # Process remaining rows

return errors  # Report all at once
```

### 5. Input Validation
- Validate early and often
- Return specific error messages
- Provide suggestions for fixes

```python
if not program_code or len(program_code) > 20:
    raise DataValidationException(
        f"Invalid program_code '{program_code}' (max 20 chars)"
    )
```

---

## Performance Optimization

### Query Optimization

```python
# Use select_related for foreign keys
slots = TimetableSlot.objects.select_related(
    'term',
    'curriculum_unit',
    'lecturer',
    'room'
).all()

# Use prefetch_related for reverse relations
conflicts = TimetableConflict.objects.prefetch_related(
    'slot_a__lecturer',
    'slot_b__room'
).all()

# Use only() to retrieve specific fields
terms = AcademicTerm.objects.only('id', 'academic_year', 'semester')
```

### Batch Operations

```python
# Bulk create for performance
slots = [
    TimetableSlot(...),
    TimetableSlot(...),
]
TimetableSlot.objects.bulk_create(slots, batch_size=100)

# Bulk duplicate check
existing = set(
    TimetableSlot.objects
    .filter(term_id=term_id)
    .values_list('id', flat=True)
)
```

### Caching

```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def get_conflicts_view(request):
    conflicts = TimetableConflict.objects.all()
    return Response(conflicts)
```

---

## Testing Strategy

### Unit Tests
```python
# tests/test_validators.py
class TestExcelValidator(TestCase):
    def test_validate_file_extension_xlsx(self):
        ExcelFileValidator.validate_file_extension("file.xlsx")
        # Should not raise
    
    def test_validate_file_extension_invalid(self):
        with self.assertRaises(FileValidationException):
            ExcelFileValidator.validate_file_extension("file.csv")
```

### Integration Tests
```python
# tests/test_upload_pipeline.py
class TestUploadPipeline(TestCase):
    def test_successful_upload(self):
        # Create test file, upload, verify results
```

### End-to-End Tests
```python
# tests/test_api.py
class TestUploadAPI(APITestCase):
    def test_upload_endpoint(self):
        with open("test_timetable.xlsx", "rb") as f:
            response = self.client.post(
                "/api/timetable/upload/",
                {"file": f},
                HTTP_AUTHORIZATION="Bearer token"
            )
        self.assertEqual(response.status_code, 201)
```

---

## Deployment Considerations

### Environment Setup
```python
# settings.py
TIMETABLE_SETTINGS = {
    'UPLOAD_MAX_SIZE': os.getenv('TIMETABLE_MAX_SIZE', 10 * 1024 * 1024),
    'BATCH_SIZE': os.getenv('TIMETABLE_BATCH_SIZE', 100),
    'CACHE_TIMEOUT': os.getenv('TIMETABLE_CACHE_TIMEOUT', 3600),
}
```

### Monitoring & Logging
```python
# Log all uploads for audit
logger.info(f"Upload completed: {upload_batch.id}")

# Monitor conflict detection performance
import time
start = time.time()
conflicts = conflict_service.detect(slots)
duration = time.time() - start
logger.info(f"Conflict detection took {duration:.2f}s for {len(slots)} slots")
```

### Scaling Considerations
- Use PostgreSQL for better concurrency
- Enable connection pooling (PgBouncer)
- Consider async tasks for large uploads (Celery)
- Monitor database query performance

---

## Future Enhancements

1. **Async Upload Processing** - Use Celery for background job processing
2. **Incremental Updates** - Track changes, update only modified slots
3. **Bulk Conflict Resolution** - Automated conflict resolution suggestions
4. **Export Functionality** - Generate timetable reports (PDF, Excel)
5. **Integration APIs** - Connect with student/lecturer apps
6. **Advanced Analytics** - Timetable utilization reports
7. **Mobile Support** - Mobile-friendly API responses
8. **Real-time Notifications** - Notify users of conflicts/updates

---

## Support & Maintenance

### Regular Maintenance
- Monitor disk usage for uploaded files
- Archive old upload batches
- Optimize database indexes periodically
- Review and clean up error logs

### Backup Strategy
- Daily database backups
- Weekly full backups
- Off-site backup storage
- Test restore procedures regularly
