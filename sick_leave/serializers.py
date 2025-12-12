#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from rest_framework import serializers

from .models import SickLeave


class SickLeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = SickLeave
        fields = "__all__"
