#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
import datetime
import os
import re
import json

import numpy as np
from datetime import datetime
from django.db.models.functions import ExtractMonth
from django.db.models import Count
from django.conf import settings
from PIL import Image
from rest_framework import status, views, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.decorators import action
import uuid
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from doc_mobile.models import DocMobile

from .models import AffiliationAVC09
from .processing.ocr_logic import (
    extract_fields_by_position,
)
from .processing.qr_reader import read_qr_from_image
from .processing.utils import correct_img, find_initial_points, pdf_to_images
from .serializers import AffiliationAVC09Serializer
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=1)


class UploadAndProcessView(views.APIView):

    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response(
                {"error": "No se envió archivo"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Guardar archivo
        filename = file_obj.name
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        save_path = os.path.join(settings.MEDIA_ROOT, filename)
        with open(save_path, "wb+") as f:
            for chunk in file_obj.chunks():
                f.write(chunk)

        # Convertir a imagen (maneja PDF también)
        pil_images = pdf_to_images(save_path)
        pil_img = pil_images[0]  # tomar primera página

        points = find_initial_points(pil_img)
        if points is None:
            points = [
                [0, 0],
                [pil_img.width, 0],
                [pil_img.width, pil_img.height],
                [0, pil_img.height],
            ]

        return Response(
            {
                "image_url": request.build_absolute_uri(settings.MEDIA_URL + filename),
                "initial_points": points.tolist(),
            },
            status=status.HTTP_200_OK,
        )


class CorrectAndOcrView(views.APIView):
    def post(self, request):
        image_url = request.data.get("image_url")
        points = request.data.get("points")
        imageSize = request.data.get("imageSize")
        displaySize = request.data.get("displaySize")

        if not image_url or not points:
            return Response(
                {"error": "Faltan parámetros"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener ruta
        if image_url.startswith(request.build_absolute_uri(settings.MEDIA_URL)):
            filename = image_url.split(settings.MEDIA_URL)[-1]
            file_path = os.path.join(settings.MEDIA_ROOT, filename)
        else:
            return Response(
                {"error": "URL no válida"}, status=status.HTTP_400_BAD_REQUEST
            )

        pil_img = Image.open(file_path).convert("RGB")

        # Aplicar corrección de perspectiva
        try:
            points = [[float(p["x"]), float(p["y"])] for p in points]
        except Exception as e:
            return Response(
                {"error": f"Formato de puntos inválido: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        warped_img = correct_img(
            pil_img, np.array(points, dtype="float32"), imageSize, displaySize
        )
        if warped_img is None:
            return Response(
                {"error": "No se pudo corregir la imagen"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ejecutar OCR
        qr_data = read_qr_from_image(pil_img)
        future = executor.submit(extract_fields_by_position, warped_img, qr_data)
        data = future.result()

        return Response(data, status=status.HTTP_200_OK)


class AffiliationAVC09ViewSet(viewsets.ModelViewSet):
    queryset = AffiliationAVC09.objects.all()

    serializer_class = AffiliationAVC09Serializer

    def update(self, request, *args, **kwargs):
        partial = True  # permite actualizaciones parciales SIEMPRE
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return super().partial_update(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user_created=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user_modified=self.request.user)

    @action(detail=False, methods=["get"])
    def count_delivery(self, request):
        count = self.get_queryset().filter(state="ENTREGAR").count()

        return Response({"count": count})

    @action(detail=False, methods=["get"])
    def get_statics(self, request, format=None):
        current_year = datetime.now().year
        year = request.query_params.get("year", current_year)

        try:
            year = int(year)
        except ValueError:
            return Response(
                {"error": "El parámetro 'year' debe ser un número entero."}, status=400
            )

        monthly_stats = (
            AffiliationAVC09.objects.filter(isue_date__year=year)
            .annotate(month=ExtractMonth("isue_date"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )
        stats_by_month = {i: 0 for i in range(1, 13)}

        for item in monthly_stats:
            stats_by_month[item["month"]] = item["count"]

        data = [stats_by_month[i] for i in range(1, 13)]

        return Response({"year": year, "extended_leaves_monthly_count": data})

    @action(detail=False, methods=["get"])
    def get_top_units(self, request, *args, **kwargs):
        top_units_data = (
            AffiliationAVC09.objects.select_related("personnel__current_destination")
            .values("personnel__current_destination__name")
            .annotate(casualty_count=Count("personnel__current_destination__name"))
            .filter(personnel__current_destination__name__isnull=False)
            .order_by("-casualty_count")[:10]
        )

        units_names = [
            item["personnel__current_destination__name"] for item in top_units_data
        ]
        casualty_counts = [item["casualty_count"] for item in top_units_data]

        response_data = {
            "units": units_names,
            "counts": casualty_counts,
        }

        return Response(response_data)


class GenerateMobileTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Generamos un UUID único
        otp_token = str(uuid.uuid4())

        # Guardamos en caché: Clave=Token, Valor=User_ID. Expira en 300 seg (5 min)
        cache.set(f"mobile_auth_{otp_token}", request.user.id, timeout=300)

        return Response({"token": otp_token})


# 2. Canjear Token Mágico por JWT (Llamado por Móvil)
class ExchangeMobileTokenView(APIView):
    permission_classes = [AllowAny]  # Importante: El móvil aún no tiene sesión

    def post(self, request):
        otp_token = request.data.get("token")

        if not otp_token:
            print("DEBUG: Falta el token OTP en la solicitud.")
            return Response({"error": "Token requerido"}, status=400)

        print(f"DEBUG: Token recibido: {otp_token}")
        cache_key = f"mobile_auth_{otp_token}"
        # Buscar en caché
        user_id = cache.get(cache_key)

        if not user_id:
            print(f"DEBUG: FALLO de CACHE para la clave: {cache_key}")
            print("DEBUG: El token no fue encontrado, expiró, o Redis no responde.")
            return Response({"error": "Token inválido o expirado"}, status=400)

        # Opcional: Borrar el token para que sea de un solo uso estricto
        cache.delete(cache_key)

        # Buscar el usuario (asumiendo modelo User por defecto)
        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=404)

        # Generar JWT manualmente
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        )


# 3. Subida desde Móvil y Notificación a PC
class MobileUploadView(APIView):
    permission_classes = [IsAuthenticated]  # Ahora sí requerimos auth

    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        session_id = request.data.get("session_id")

        if not file or not session_id:
            return Response(
                {"error": "Faltan datos"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            document = DocMobile.objects.create(
                user=request.user,
                file=file,
                session_id=session_id,
            )
            save_path = document.file.path
            image_url = request.build_absolute_uri(document.file.url)

            pil_images = pdf_to_images(save_path)
            if not pil_images:
                return Response(
                    {
                        "error": "No se pudo procesar el archivo (no es una imagen o PDF válido)."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            pil_img = pil_images[0]

            initial_points = find_initial_points(pil_img)

            if initial_points is None:
                initial_points = [
                    [0, 0],
                    [pil_img.width, 0],
                    [pil_img.width, pil_img.height],
                    [0, pil_img.height],
                ]
            if isinstance(initial_points, np.ndarray):
                initial_points = initial_points.tolist()

            # NOTE: Notificar al WebSocket
            channel_layer = get_channel_layer()
            group_name = f"upload_{session_id}"

            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "image_uploaded",  # NOTE: DEBE COINCIDIR con el consumer y el frontend
                    "image_url": image_url,
                    "initial_points": initial_points,
                },
            )
            return Response(
                {"message": "Archivo recibido y notificado."}, status=status.HTTP_200_OK
            )

        except Exception as e:
            print(f"Error al procesar la subida móvil: {e}")
            return Response(
                {"error": f"Error interno del servidor: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
