from rest_framework import serializers
from apps.programs.models import Program


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ("id", "department", "name", "code", "duration_years", "award_type", "description", "status", "created_at")
        read_only_fields = ("created_at",)
