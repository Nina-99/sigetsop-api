from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.views import Response
from django.db.models import Case, When, Value, IntegerField

from file_personnel.serializers import FilePersonnelSerializer
from server.pagination import CustomPersonnelPagination

from .models import FilePersonnel


# Create your views here.
class FileViewSet(viewsets.ModelViewSet):
    queryset = FilePersonnel.objects.all()
    serializer_class = FilePersonnelSerializer
    pagination_class = CustomPersonnelPagination

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                priority=Case(
                    When(documents_has__isnull=False, documents_has__exact="", then=2),
                    When(documents_has__isnull=False, then=0),
                    When(observation__isnull=False, observation__exact="", then=3),
                    When(observation__isnull=False, then=1),
                    default=Value(4),
                    output_field=IntegerField(),
                )
            )
            .order_by("priority", "personnel__last_name", "-id")
        )

    def perform_update(self, serializer):
        serializer.save(user_updated=self.request.user)

    @action(detail=False, methods=["get"])
    def count_file(self, request):
        count = (
            self.get_queryset()
            .exclude(Q(documents_has__isnull=True) | Q(documents_has__exact=""))
            .count()
        )

        return Response({"count": count})
