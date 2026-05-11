from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from apps.curriculum.models import Curriculum, CurriculumUnit, CurriculumVersion
from apps.curriculum.services import CurriculumService
from apps.curriculum.utils import get_user_department_id, is_department_admin, is_super_admin
from apps.curriculum.validators import CurriculumDomainValidator


class CurriculumVersionSerializer(serializers.ModelSerializer):
    acted_by_name = serializers.CharField(source="acted_by.get_full_name", read_only=True)

    class Meta:
        model = CurriculumVersion
        fields = [
            "id",
            "version",
            "action",
            "change_summary",
            "acted_by",
            "acted_by_name",
            "created_at",
        ]
        read_only_fields = fields


class CurriculumSerializer(serializers.ModelSerializer):
    units = serializers.ListField(child=serializers.DictField(), write_only=True, required=False)
    curriculum_units = serializers.SerializerMethodField(read_only=True)
    version_history = CurriculumVersionSerializer(many=True, read_only=True)

    class Meta:
        model = Curriculum
        fields = [
            "id",
            "program",
            "department",
            "academic_year",
            "study_year",
            "semester",
            "version",
            "status",
            "created_by",
            "created_at",
            "updated_at",
            "units",
            "curriculum_units",
            "version_history",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at", "version_history"]

    def validate(self, attrs):
        program = attrs.get("program") or getattr(self.instance, "program", None)
        department = attrs.get("department") or getattr(self.instance, "department", None)

        if program and department and program.department_id != department.id:
            raise serializers.ValidationError(
                {"department": "Department must match the selected program's department."}
            )

        request = self.context.get("request")
        if request and is_department_admin(request.user) and not is_super_admin(request.user):
            user_department_id = get_user_department_id(request.user)
            if department and department.id != user_department_id:
                raise serializers.ValidationError(
                    {"department": "Department admins can only manage curriculum in their department."}
                )

        semester = attrs.get("semester")
        if semester is not None:
            CurriculumDomainValidator.validate_semester(semester)

        units_payload = self.initial_data.get("units")
        if units_payload is not None:
            if not isinstance(units_payload, list):
                raise serializers.ValidationError({"units": "Units payload must be a list."})
            CurriculumDomainValidator.validate_duplicate_units(units_payload)

        return attrs

    def create(self, validated_data):
        units_payload = validated_data.pop("units", [])
        actor = self.context["request"].user
        try:
            return CurriculumService.create_curriculum(
                payload={
                    "program": validated_data["program"].id,
                    "department": validated_data["department"].id,
                    "academic_year": validated_data["academic_year"],
                    "study_year": validated_data["study_year"],
                    "semester": validated_data["semester"],
                    "version": validated_data.get("version", 1),
                    "status": validated_data.get("status", Curriculum.Status.ACTIVE),
                },
                units_payload=units_payload,
                actor=actor,
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(getattr(exc, "message_dict", exc.messages))

    def update(self, instance, validated_data):
        units_payload = validated_data.pop("units", None)
        actor = self.context["request"].user
        payload = {}
        for key, value in validated_data.items():
            if hasattr(value, "id"):
                payload[key] = value.id
            else:
                payload[key] = value

        try:
            return CurriculumService.update_curriculum(
                curriculum=instance,
                payload=payload,
                units_payload=units_payload,
                actor=actor,
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(getattr(exc, "message_dict", exc.messages))

    def get_curriculum_units(self, obj):
        queryset = obj.curriculum_units.select_related("unit", "prerequisite_unit").order_by(
            "display_order", "unit__code"
        )
        return CurriculumUnitSerializer(queryset, many=True).data


class CurriculumUnitSerializer(serializers.ModelSerializer):
    curriculum_program = serializers.CharField(source="curriculum.program.code", read_only=True)
    curriculum_study_year = serializers.IntegerField(source="curriculum.study_year", read_only=True)
    curriculum_semester = serializers.IntegerField(source="curriculum.semester", read_only=True)

    class Meta:
        model = CurriculumUnit
        fields = [
            "id",
            "curriculum",
            "curriculum_program",
            "curriculum_study_year",
            "curriculum_semester",
            "unit",
            "is_core",
            "is_elective",
            "display_order",
            "prerequisite_unit",
            "credit_hours",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        is_core = attrs.get("is_core", getattr(self.instance, "is_core", True))
        is_elective = attrs.get("is_elective", getattr(self.instance, "is_elective", False))

        if is_core and is_elective:
            raise serializers.ValidationError("A unit cannot be both core and elective.")
        if not is_core and not is_elective:
            raise serializers.ValidationError("A unit must be core or elective.")
        return attrs
