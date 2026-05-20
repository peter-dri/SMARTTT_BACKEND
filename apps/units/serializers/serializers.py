from rest_framework import serializers
from apps.units.models import Unit


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ("id", "code", "name", "credit_hours", "description", "department", "status")
