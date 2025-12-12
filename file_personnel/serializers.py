#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from rest_framework import serializers

from grades.models import Grade
from police_personnel.models import Personnel
from police_unit.models import Units

from .models import FilePersonnel


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ["id", "grade_abbr"]


class UnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Units
        fields = ["id", "name", "assistant"]


class PersonnelSerializer(serializers.ModelSerializer):
    grade_data = GradeSerializer(source="grade", read_only=True)
    units_data = UnitsSerializer(source="current_destination", read_only=True)

    grade = serializers.PrimaryKeyRelatedField(
        queryset=Grade.objects.all(), write_only=True, required=False, allow_null=True
    )
    current_destination = serializers.PrimaryKeyRelatedField(
        queryset=Units.objects.all(), write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Personnel
        fields = [
            "id",
            "grade_data",
            "grade",
            "first_name",
            "middle_name",
            "last_name",
            "maternal_name",
            "identity_card",
            "units_data",
            "insured_number",
            "current_destination",
        ]


class FilePersonnelSerializer(serializers.ModelSerializer):
    personnel_data = PersonnelSerializer(source="personnel", read_only=True)

    personnel = serializers.PrimaryKeyRelatedField(
        queryset=Personnel.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = FilePersonnel
        fields = [
            "id",
            "has_file",
            "personnel_data",
            "personnel",
            "documents_has",
            "observation",
        ]
