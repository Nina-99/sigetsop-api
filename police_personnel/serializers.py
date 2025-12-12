#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from datetime import date
from rest_framework import serializers

from grades.models import Grade
from police_unit.models import Units

from .models import Personnel


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
    age = serializers.SerializerMethodField()
    years_age = serializers.SerializerMethodField()

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
            "age",
            "birthdate",
            "genre",
            "phone",
            "years_age",
            "joining_police",
            "scale",
            "insured_number",
            "units_data",
            "current_destination",
            "address",
            "door_number",
            "area",
            "reference",
            "reference_phone",
            "is_active",
        ]
        extra_kwargs = {
            "middle_name": {"required": False, "allow_blank": True},
            "maternal_name": {"required": False, "allow_blank": True},
            "phone": {"required": False, "allow_blank": True},
            "scale": {"required": False, "allow_blank": True},
            "insured_number": {
                "required": False,
                "allow_blank": True,
            },
            "address": {"required": False, "allow_blank": True},
            "door_number": {"required": False, "allow_blank": True},
            "area": {"required": False, "allow_blank": True},
            "reference": {"required": False, "allow_blank": True},
            "reference_phone": {"required": False, "allow_blank": True},
            "genre": {"required": False, "allow_blank": True},
            "is_active": {"required": False},
        }

    def validate_first_name(self, value):
        return value.upper().strip() if value else value

    def validate_last_name(self, value):
        return value.upper().strip() if value else value

    def validate_maternal_name(self, value):
        return value.upper().strip() if value else value

    def validate_middle_name(self, value):
        return value.upper().strip() if value else value

    def validate_insured_number(self, value):
        if not value or value.strip() == "":
            return None
        return value.strip().upper()

    def get_age(self, obj):
        if not obj.birthdate:
            return None
        today = date.today()
        return (
            today.year
            - obj.birthdate.year
            - ((today.month, today.day) < (obj.birthdate.month, obj.birthdate.day))
        )

    def get_years_age(self, obj):
        if not obj.joining_police:
            return None
        today = date.today()
        return (
            today.year
            - obj.joining_police.year
            - (
                (today.month, today.day)
                < (obj.joining_police.month, obj.joining_police.day)
            )
        )
