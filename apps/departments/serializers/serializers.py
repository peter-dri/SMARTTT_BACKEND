from rest_framework import serializers
from apps.departments.models import Faculty, Department, DepartmentAdmin


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ("id", "name", "code", "description")


class DepartmentSerializer(serializers.ModelSerializer):
    faculty = FacultySerializer(read_only=True)
    faculty_id = serializers.PrimaryKeyRelatedField(queryset=Faculty.objects.all(), source="faculty", write_only=True)

    class Meta:
        model = Department
        fields = ("id", "faculty", "faculty_id", "name", "code", "description", "head_of_department", "status", "created_at")
        read_only_fields = ("created_at",)


class DepartmentAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentAdmin
        fields = ("id", "user", "department", "role", "assigned_at")
        read_only_fields = ("assigned_at",)
