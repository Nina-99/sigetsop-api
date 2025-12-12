#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from django.shortcuts import render
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import Response

from .models import Grade
from .serializers import GradeSerializer


# Create your views here.
class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.filter(deleted_at__isnull=True)
    serializer_class = GradeSerializer
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
            {"detail": "Grade deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )

    def get_queryset(self):
        if self.request.query_params.get("show_deleted") == "true":
            return Grade.objects.all()
        return Grade.objects.filter(deleted_at__isnull=True)
