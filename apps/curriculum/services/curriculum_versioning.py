from django.db import transaction

from apps.curriculum.models import Curriculum, CurriculumVersion


class CurriculumVersioningService:
    """Handles lifecycle operations around curriculum versions."""

    @staticmethod
    @transaction.atomic
    def create_version_entry(*, curriculum: Curriculum, action: str, acted_by=None, summary: str = ""):
        return CurriculumVersion.objects.create(
            curriculum=curriculum,
            version=curriculum.version,
            action=action,
            acted_by=acted_by,
            change_summary=summary,
        )

    @classmethod
    @transaction.atomic
    def activate_curriculum(cls, *, curriculum: Curriculum, acted_by=None, summary: str = ""):
        Curriculum.objects.filter(
            program_id=curriculum.program_id,
            academic_year=curriculum.academic_year,
            study_year=curriculum.study_year,
            semester=curriculum.semester,
        ).exclude(id=curriculum.id).update(status=Curriculum.Status.INACTIVE)

        curriculum.status = Curriculum.Status.ACTIVE
        curriculum.save(update_fields=["status", "updated_at"])
        cls.create_version_entry(
            curriculum=curriculum,
            action=CurriculumVersion.Action.ACTIVATED,
            acted_by=acted_by,
            summary=summary,
        )
        return curriculum

    @classmethod
    @transaction.atomic
    def deactivate_curriculum(cls, *, curriculum: Curriculum, acted_by=None, summary: str = ""):
        curriculum.status = Curriculum.Status.INACTIVE
        curriculum.save(update_fields=["status", "updated_at"])
        cls.create_version_entry(
            curriculum=curriculum,
            action=CurriculumVersion.Action.DEACTIVATED,
            acted_by=acted_by,
            summary=summary,
        )
        return curriculum

    @classmethod
    @transaction.atomic
    def bump_version(cls, *, curriculum: Curriculum, acted_by=None, summary: str = ""):
        curriculum.version += 1
        curriculum.save(update_fields=["version", "updated_at"])
        cls.create_version_entry(
            curriculum=curriculum,
            action=CurriculumVersion.Action.UPDATED,
            acted_by=acted_by,
            summary=summary,
        )
        return curriculum