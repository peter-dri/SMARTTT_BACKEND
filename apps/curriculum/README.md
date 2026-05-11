# Curriculum Management Module

Production-grade curriculum intelligence layer for SMARTTT backend.

## Folder Structure

```text
apps/curriculum/
├── admin.py
├── apps.py
├── migrations/
│   └── 0001_initial.py
├── models/
│   ├── __init__.py
│   └── curriculum.py
├── permissions/
│   ├── __init__.py
│   └── access.py
├── serializers/
│   ├── __init__.py
│   └── curriculum_serializer.py
├── services/
│   ├── __init__.py
│   ├── curriculum_mapper.py
│   ├── curriculum_service.py
│   └── curriculum_versioning.py
├── tests/
│   ├── __init__.py
│   └── test_curriculum_api.py
├── urls.py
├── utils/
│   ├── __init__.py
│   └── access.py
├── validators/
│   ├── __init__.py
│   └── curriculum_validator.py
└── views/
    ├── __init__.py
    └── curriculum_viewset.py
```

## Architecture Overview

- Models: persistence and relational integrity only.
- Validators: domain rules (duplicate units, semester validity, required core units, duplicate versions).
- Services: orchestration and business logic.
  - `CurriculumService`: create/update workflows and unit replacement.
  - `CurriculumMapperService`: student -> program/year/semester -> required units.
  - `CurriculumVersioningService`: activation/deactivation/version events.
- Permissions: department-scoped write, student read-only, super admin full access.
- Views: thin class-based APIs delegating to services.

## Endpoints

Base path in project: `/api/v1/curriculum/`

- `POST /api/v1/curriculum/`
- `GET /api/v1/curriculum/`
- `GET /api/v1/curriculum/{id}/`
- `PUT /api/v1/curriculum/{id}/`
- `DELETE /api/v1/curriculum/{id}/`
- `GET /api/v1/curriculum/student-units/`

## API Response Examples

### Create Curriculum (POST)

Request body:

```json
{
  "program": "3cb91f52-2e78-4e62-b85f-2f30d0cc7be5",
  "department": "6f6b3395-38a2-495c-97ff-f8f38f3859d8",
  "academic_year": "2025/2026",
  "study_year": 2,
  "semester": 1,
  "version": 1,
  "status": "active",
  "units": [
    {
      "unit": "9f1d67d0-d8a3-4990-badf-f69b9d8bcb14",
      "is_core": true,
      "is_elective": false,
      "display_order": 1,
      "credit_hours": 3
    }
  ]
}
```

Response:

```json
{
  "id": "8fc67fb2-e8f4-4327-aa43-cd8610f4fb8d",
  "program": "3cb91f52-2e78-4e62-b85f-2f30d0cc7be5",
  "department": "6f6b3395-38a2-495c-97ff-f8f38f3859d8",
  "academic_year": "2025/2026",
  "study_year": 2,
  "semester": 1,
  "version": 1,
  "status": "active",
  "created_by": "7efea3e6-2be2-44ff-ae36-38870f81e738",
  "created_at": "2026-05-11T12:30:00Z",
  "updated_at": "2026-05-11T12:30:00Z",
  "curriculum_units": [
    {
      "id": "6f576a16-f840-488b-85a2-b6dc8d169f31",
      "curriculum": "8fc67fb2-e8f4-4327-aa43-cd8610f4fb8d",
      "curriculum_program": "BCS",
      "curriculum_study_year": 2,
      "curriculum_semester": 1,
      "unit": "9f1d67d0-d8a3-4990-badf-f69b9d8bcb14",
      "is_core": true,
      "is_elective": false,
      "display_order": 1,
      "prerequisite_unit": null,
      "credit_hours": 3,
      "created_at": "2026-05-11T12:30:00Z",
      "updated_at": "2026-05-11T12:30:00Z"
    }
  ],
  "version_history": []
}
```

### Student Units (GET /student-units/)

```json
{
  "student_id": "dd0b39af-924d-4fa5-a7be-2df627eb6d53",
  "program_id": "3cb91f52-2e78-4e62-b85f-2f30d0cc7be5",
  "academic_year": "2025/2026",
  "study_year": 2,
  "semester": 1,
  "curriculum_id": "8fc67fb2-e8f4-4327-aa43-cd8610f4fb8d",
  "curriculum_version": 1,
  "units": [
    {
      "curriculum_unit_id": "6f576a16-f840-488b-85a2-b6dc8d169f31",
      "unit_id": "9f1d67d0-d8a3-4990-badf-f69b9d8bcb14",
      "unit_code": "CSC201",
      "unit_title": "Data Structures",
      "credit_hours": 3,
      "is_core": true,
      "is_elective": false,
      "display_order": 1,
      "prerequisite_unit_id": null,
      "prerequisite_unit_code": null
    }
  ]
}
```

## Suggested Migration Order

Given this repository currently has little/no app migrations tracked, recommended order:

1. `accounts`
2. `departments`
3. `programs`
4. `units`
5. `students`
6. `lecturers`
7. `curriculum`
8. `timetable`
9. `enrollments`
10. `rooms`
11. `analytics`

If starting fresh: run `makemigrations` for all apps, then `migrate`.
