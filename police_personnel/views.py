#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from django.db.models import Q, Value
from rest_framework import viewsets, status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import Response
from django.shortcuts import get_object_or_404
from django.db.models import Case, When, IntegerField

from server.pagination import CustomPersonnelPagination
from .models import Personnel
from .serializers import PersonnelSerializer


class PersonnelSearchAPIView(ListAPIView):
    serializer_class = PersonnelSerializer
    pagination_class = CustomPersonnelPagination

    def get_queryset(self):
        insured_number = self.request.query_params.get("insuredNumber", "").strip()
        full_name = self.request.query_params.get("fullName", "").strip()
        q_general = self.request.query_params.get("q", "").strip()
        filter_status = (
            self.request.query_params.get("filter_status", "True").lower() == "true"
        )

        qs = Personnel.objects.filter(is_active=filter_status)

        # 🔹 1️⃣ Primero buscar por insured_number exacto
        if insured_number:
            qs_insured = qs.filter(insured_number__iexact=insured_number)
            if qs_insured.exists():
                return qs_insured

        # 🔹 2️⃣ Buscar por full_name priorizando apellidos y luego nombre
        if full_name:
            terms = full_name.split()
            qs_name = qs
            for t in terms:
                qs_name = qs_name.filter(
                    Q(last_name__icontains=t)
                    | Q(maternal_name__icontains=t)
                    | Q(first_name__icontains=t)
                )
            if qs_name.exists():
                return qs_name

        # 🔹 3️⃣ Búsqueda general
        if q_general:
            terms = q_general.split()
            qs_general = qs
            for t in terms:
                qs_general = qs_general.filter(
                    Q(insured_number__icontains=t)
                    | Q(last_name__icontains=t)
                    | Q(maternal_name__icontains=t)
                    | Q(first_name__icontains=t)
                )
            return qs_general

        return qs.order_by("last_name", "maternal_name", "first_name")


class PersonnelViewSet(viewsets.ModelViewSet):
    queryset = Personnel.objects.all()
    serializer_class = PersonnelSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPersonnelPagination

    def get_queryset(self):
        queryset = Personnel.objects.all().prefetch_related(
            "grade", "current_destination"
        )

        search_term = self.request.query_params.get("search", None)
        filter_status = (
            self.request.query_params.get("filter_status", "True").lower() == "true"
        )

        # Filtrar por estado
        queryset = queryset.filter(is_active=filter_status)

        # Búsqueda prioritaria si se ingresa search_term
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
                        Q(last_name__icontains=first_term)
                        & Q(last_name__icontains=last_term),
                        then=Value(0),
                    ),
                    When(last_name__icontains=first_term, then=Value(1)),
                    When(maternal_name__icontains=first_term, then=Value(2)),
                    When(first_name__icontains=first_term, then=Value(3)),
                    When(identity_card__icontains=first_term, then=Value(4)),
                    When(
                        current_destination__name__icontains=first_term, then=Value(5)
                    ),
                    default=Value(6),
                    output_field=IntegerField(),
                )
            ).filter(
                Q(last_name__icontains=search)
                | Q(maternal_name__icontains=search)
                | Q(first_name__icontains=search)
                | Q(identity_card__icontains=search)
                | Q(current_destination__name__icontains=search)
            )
        return queryset.order_by(
            "search_priority", "last_name", "maternal_name", "first_name"
        )

    def get_object(self):
        queryset = Personnel.objects.all()
        return get_object_or_404(queryset, pk=self.kwargs["pk"])

    def perform_create(self, serializer):
        serializer.save(user_created=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user_update=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
