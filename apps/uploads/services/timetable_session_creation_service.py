from __future__ import annotations

from django.db import transaction

from apps.timetable.models import TimetableSession


class TimetableSessionCreationService:
    @staticmethod
    @transaction.atomic
    def bulk_create_sessions(session_payloads: list[dict]) -> list[TimetableSession]:
        sessions = [TimetableSession(**payload) for payload in session_payloads]
        created_sessions = TimetableSession.objects.bulk_create(sessions, batch_size=500)
        return list(created_sessions)