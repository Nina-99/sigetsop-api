#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from rest_framework import serializers

from .models import AffiliationAVC07


class AffiliationAVC07Serializer(serializers.ModelSerializer):
    class Meta:
        model = AffiliationAVC07
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "deleted_at")
