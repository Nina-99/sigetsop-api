#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response
from django.shortcuts import get_object_or_404

from server.pagination import CustomPersonnelPagination

from .models import Personnel
from .serializers import PersonnelSerializer


class PersonnelSearchAPIView(ListAPIView):
    serializer_class = PersonnelSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        insured_number = self.request.query_params.get("insuredNumber", "").strip()
        full_name = self.request.query_params.get("fullName", "").strip()
        q_general = self.request.query_params.get("q", "").strip()

        if insured_number:
            qs = Personnel.objects.filter(insured_number__iexact=insured_number)
            if qs.exists():
                return qs

        if full_name:
            terms = full_name.split()
            qs = Personnel.objects.all()
            for t in terms:
                qs = qs.filter(
                    Q(first_name__icontains=t)
                    | Q(last_name__icontains=t)
                    | Q(maternal_name__icontains=t)
                )
            if qs.exists():
                return qs

        if q_general:
            terms = q_general.split()
            qs = Personnel.objects.all()
            for t in terms:
                qs = qs.filter(
                    Q(first_name__icontains=t)
                    | Q(last_name__icontains=t)
                    | Q(maternal_name__icontains=t)
                    | Q(insured_number__icontains=t)
                )
            return qs


# Create your views here.
class PersonnelViewSet(viewsets.ModelViewSet):
    queryset = Personnel.objects.all()
    serializer_class = PersonnelSerializer
    permission_classes = [IsAuthenticated]

    pagination_class = CustomPersonnelPagination

    def get_queryset(self):
        queryset = Personnel.objects.all()

        search_term = self.request.query_params.get("search", None)

        if search_term:

            queryset = queryset.filter(
                Q(last_name__icontains=search_term)
                | Q(maternal_name__icontains=search_term)
                | Q(first_name__icontains=search_term)
                | Q(identity_card__icontains=search_term)
                | Q(units_data__name__icontains=search_term)
            )

        return queryset.order_by("last_name")

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
