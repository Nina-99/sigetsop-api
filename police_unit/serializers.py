#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from rest_framework import serializers

from grades.models import Grade
from police_personnel.models import Personnel

from .models import Units


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ["id", "grade_abbr"]


class PersonnelSerializer(serializers.ModelSerializer):
    grade_data = GradeSerializer(source="grade", read_only=True)

    grade = serializers.PrimaryKeyRelatedField(
        queryset=Grade.objects.all(), write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Personnel
        fields = [
            "id",
            "grade_data",
            "grade",
            "last_name",
            "maternal_name",
            "first_name",
            "middle_name",
            "phone",
        ]


class UnitsSerializers(serializers.ModelSerializer):
    commander_data = PersonnelSerializer(source="commander", read_only=True)
    assistant_data = PersonnelSerializer(source="assistant", read_only=True, many=True)

    commander = serializers.PrimaryKeyRelatedField(
        queryset=Personnel.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    assistant = serializers.PrimaryKeyRelatedField(
        queryset=Personnel.objects.all(),
        write_only=True,
        many=True,
        required=False,
    )

    class Meta:
        model = Units
        fields = [
            "id",
            "name",
            "commander",
            "commander_data",  # Comandante
            "assistant",
            "assistant_data",  # Asistentes
        ]

    def create(self, validated_data):
        assistants = validated_data.pop("assistant", [])
        instance = super().create(validated_data)
        if assistants:
            instance.assistant.set(assistants)
        instance.refresh_from_db()
        return instance

    def update(self, instance, validated_data):
        assistants = validated_data.pop("assistant", None)
        instance = super().update(instance, validated_data)

        if assistants is not None:
            instance.assistant.set(assistants)

        instance.refresh_from_db()

        return instance
