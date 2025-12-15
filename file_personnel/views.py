#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
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
    serializer_class = FilePersonnelSerializer
    pagination_class = CustomPersonnelPagination

    def get_queryset(self):
        queryset = (
            FilePersonnel.objects.select_related(
                "personnel", "personnel__grade", "personnel__current_destination"
            ).annotate(
                priority=Case(
                    When(documents_has__isnull=False, documents_has__exact="", then=2),
                    When(documents_has__isnull=False, then=0),
                    When(observation__isnull=False, observation__exact="", then=3),
                    When(observation__isnull=False, then=1),
                    default=Value(4),
                    output_field=IntegerField(),
                )
            )
            # .order_by("priority", "personnel__last_name", "-id")
        )

        queryset = queryset.annotate(
            search_priority=Value(99, output_field=IntegerField())
        )

        search = self.request.query_params.get("search", "").strip()
        if search:
            terms = [t for t in search.split() if t]

            first_term = terms[0]
            last_term = terms[-1] if len(terms) > 1 else terms[0]

            queryset = queryset.annotate(
                search_priority=Case(
                    When(
                        Q(personnel__last_name__icontains=first_term)
                        & Q(personnel__last_name__icontains=last_term),
                        then=Value(0),
                    ),
                    When(personnel__last_name__icontains=first_term, then=Value(1)),
                    When(personnel__maternal_name__icontains=first_term, then=Value(2)),
                    When(personnel__first_name__icontains=first_term, then=Value(3)),
                    default=Value(4),
                    output_field=IntegerField(),
                )
            ).filter(
                Q(personnel__last_name__icontains=search)
                | Q(personnel__maternal_name__icontains=search)
                | Q(personnel__first_name__icontains=search)
            )

        return queryset.order_by(
            "search_priority",
            "priority",
            "personnel__last_name",
            "personnel__maternal_name",
            "-id",
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
