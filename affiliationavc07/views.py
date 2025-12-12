#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from django.shortcuts import render
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import Response

from .models import AffiliationAVC07
from .serializers import AffiliationAVC07Serializer


# Create your views here.
class AffiliationAVC07ViewSet(viewsets.ModelViewSet):
    queryset = AffiliationAVC07.objects.all().order_by("-created_at")
    serializer_class = AffiliationAVC07Serializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user_created=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user_updated=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = timezone.now()
        instance.user_deleted = request.user
        instance.save()
        return Response(
            {"detail": "AffiliationAVC07 deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )

    def get_queryset(self):
        if self.request.query_params.get("show_deleted") == "true":
            return Grade.objects.all()
        return Grade.objects.filter(deleted_at__isnull=True)
