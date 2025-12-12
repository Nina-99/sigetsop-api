#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import Response
from django.db.models import Count, Case, When, IntegerField, Q

from .models import Units
from .serializers import UnitsSerializers


# Create your views here.
class UnitsViewSet(viewsets.ModelViewSet):
    # queryset = Units.objects.all().order_by("-created_at")
    queryset = Units.objects.filter(deleted_at__isnull=True).order_by("name")

    serializer_class = UnitsSerializers
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user_created=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user_updated=self.request.user)

    # def perform_create(self, serializer):
    #     serializer.save(user_created=self.request.user)
    #
    # def perform_update(self, serializer):
    #     serializer.save(user_updated=self.request.user)

    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     instance.deleted_at = timezone.now()
    #     instance.user_deleted = request.user
    #     instance.save()
    #     return Response(
    #         {"detail": "Police Units deleted successfully"},
    #         status=status.HTTP_204_NO_CONTENT,
    #     )

    def get_queryset(self):
        queryset = Units.objects.annotate(
            assistant_count=Count("assistant", distinct=True),
            # Prioridad:
            # 1 → tiene assistants
            # 2 → no tiene assistants pero sí commander
            # 3 → no tiene ni assistants ni commander
            priority=Case(
                When(assistant_count__gt=0, then=1),
                When(Q(assistant_count=0) & Q(commander__isnull=False), then=2),
                default=3,
                output_field=IntegerField(),
            ),
        )

        return queryset.order_by("priority", "name")
