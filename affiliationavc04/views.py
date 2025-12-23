#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
import os
import tempfile
import numpy as np

from django.core.files.storage import default_storage
from django.http.request import MultiPartParser
from django.shortcuts import render
from rest_framework import status, views, viewsets
from django.conf import settings
from PIL import Image
from rest_framework.parsers import FormParser
from rest_framework.views import APIView, Response

from .models import AffiliationAVC04
from .serializers import AffiliationAVC04Serializer

from .processing.ocr_logic import (
    extract_fields_by_position,
)
from .processing.qr_reader import read_qr_from_image
from .processing.utils import correct_img, find_initial_points, pdf_to_images
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=1)

# from .utils import process_file_and_extract


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


class AffiliationAVC04ViewSet(APIView):
    def post(self, request):
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        path = f"/tmp/{file.name}"
        with open(path, "wb+") as dest:
            for chunk in file.chunks():
                dest.write(chunk)

        # data = process_file_and_extract(path)
        # serializer = AffiliationAVC04Serializer(data=data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#
# class UploadDocumentAPIView(APIView):
#     """
#     POST: recibe file (pdf o imagen), procesa y guarda campos extraídos en BD.
#     """
#     def post(self, request, format=None):
#         f = request.FILES.get('file')
#         if not f:
#             return Response({'error': 'Se requiere un archivo'}, status=status.HTTP_400_BAD_REQUEST)
#
#         path = default_storage.save(f'media/uploads/{f.name}', f)
#         local_path = default_storage.path(path)
#
#         # procesar archivo -> extraer datos
#         result = process_file_and_extract(local_path)
#
#         # guardar en DB
#         doc = Document.objects.create(
#             original_filename=f.name,
#             raw_text=result.get('raw_text', ''),
#             apellido_paterno=result.get('apellido_paterno'),
#             apellido_materno=result.get('apellido_materno'),
#             nombre_trabajador=result.get('nombre_trabajador'),
#             numero_asegurado=result.get('numero_asegurado'),
#             fecha_nacimiento=result.get('fecha_nacimiento'),
#             sexo=result.get('sexo'),
#             zona=result.get('zona'),
#             domicilio=result.get('domicilio'),
#             salario_mensual=result.get('salario_mensual'),
#             ocupacion_actual=result.get('ocupacion_actual'),
#             fecha_ingreso=result.get('fecha_ingreso'),
#             nombre_empleador=result.get('nombre_empleador'),
#             numero_empleador=result.get('numero_empleador'),
#             localidad=result.get('localidad'),
#             confidence=result.get('confidence'),
#         )
#
#         serializer = DocumentSerializer(doc)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

# Create your views here.
# class AffiliationAVC04ViewSet(APIView):
#     # Permite subir archivos (imágenes o PDF)
#     parser_classes = (MultiPartParser, FormParser)
#
#     def post(self, request, *args, **kwargs):
#         file_obj = request.data.get("file")
#
#         if not file_obj:
#             return Response(
#                 {"error": "No se ha proporcionado un archivo."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#
#         # 1. Guardar el archivo temporalmente
#         temp_dir = "temp_uploads"
#         os.makedirs(temp_dir, exist_ok=True)
#         temp_file_path = os.path.join(temp_dir, file_obj.name)
#
#         with open(temp_file_path, "wb+") as destination:
#             for chunk in file_obj.chunks():
#                 destination.write(chunk)
#
#         try:
#             # 2. Realizar la extracción de datos
#             extracted_data = extract_text(temp_file_path)
#
#             # 3. Almacenar en la base de datos (PostgreSQL)
#             serializer = AffiliationAVC04Serializer(data=extracted_data)
#             if serializer.is_valid():
#                 instance = serializer.save()
#
#                 # 4. Devolver la respuesta exitosa
#                 response_data = AffiliationAVC04Serializer(instance).data
#                 return Response(response_data, status=status.HTTP_201_CREATED)
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#         except Exception as e:
#             return Response(
#                 {"error": f"Error en el procesamiento del OCR o RegEx: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )
#         finally:
#             # 5. Limpiar el archivo subido
#             if os.path.exists(temp_file_path):
#                 os.remove(temp_file_path)
#
# def post(self, request):
#     file = request.FILES.get("file")
#     if not file:
#         return Response({"error": "No se envió archivo"}, status=400)
#
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
#         for chunk in file.chunks():
#             tmp.write(chunk)
#         tmp_path = tmp.name
#
#     text = extract_text(tmp_path)
#     data = parse_data(text)
#
#     serializer = AffiliationAVC04Serializer(data=data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=201)
#     return Response(serializer.errors, status=400)
#     # def post(self, request, *args, **kwargs):
#     #     if "file" not in request.FILES:
#     #         return Response(
#     #             {"error": "No se proporcionó ningún archivo."},
#     #             status=status.HTTP_400_BAD_REQUEST,
#     #         )
#     #
#     #     uploaded_file = request.FILES["file"]
#     #
#     #     # --- 1. Guardar temporalmente y en el modelo ---
#     #     try:
#     #         # Crear y guardar la instancia del modelo con el archivo
#     #         doc_instance = affiliationavc04(original_file=uploaded_file)
#     #         doc_instance.save()
#     #         file_path = doc_instance.original_file.path
#     #
#     #     except Exception as e:
#     #         return Response(
#     #             {"error": f"Error al guardar el archivo: {e}"},
#     #             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#     #         )
#     #
#     #     # --- 2. Procesar OCR y Extracción ---
#     #     processing_result = extract_data_from_file(file_path)
#     #
#     #     if "error" in processing_result:
#     #         # Si hay un error de procesamiento, se puede decidir si borrar la instancia o dejarla
#     #         return Response(
#     #             {"error": processing_result["error"]},
#     #             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#     #         )
#     #
#     # --- 3. Almacenar los resultados ---
#
#     # Actualizar la instancia del modelo con los datos extraídos
#     doc_instance.extracted_text = processing_result.get("full_text", "")
#     doc_instance.nombre_completo = processing_result.get("first_name")
#     # doc_instance.numero_carnet = processing_result.get('numero_carnet')
#
#     # Convertir la fecha extraída al formato DateField de Django (YYYY-MM-DD)
#     # date_str = processing_result.get('fecha_nacimiento')
#     # if date_str:
#     #     try:
#     #         # Asumiendo formato DD/MM/AAAA o DD-MM-AAAA
#     #         date_obj = datetime.strptime(date_str, '%d/%m/%Y')
#     #         doc_instance.fecha_nacimiento = date_obj.strftime('%Y-%m-%d')
#     #     except ValueError:
#     #         # Si el formato no coincide, se guarda como None y se registra el error
#     #         print(f"Advertencia: Formato de fecha no reconocido: {date_str}")
#     #         doc_instance.fecha_nacimiento = None
#
#     doc_instance.save()
#
#     return Response(
#         {
#             "message": "Archivo procesado y datos extraídos correctamente.",
#             "data": {
#                 "id": doc_instance.id,
#                 "first_name": doc_instance.nombre_completo,
#                 # "fecha_nacimiento": doc_instance.fecha_nacimiento,
#                 # "numero_carnet": doc_instance.numero_carnet
#             },
#         },
#         status=status.HTTP_201_CREATED,
#     )
#
# # queryset = AffiliationAVC04.objects.all().order_by("-created_at")
# # serializer_class = AffiliationAVC04Serializer
# # permission_classes = [IsAuthenticated]
# #
# # def perform_create(self, serializer):
# #     serializer.save(user_created=self.request.user)
# #
# # def perform_update(self, serializer):
# #     serializer.save(user_updated=self.request.user)
# #
# # def destroy(self, request, *args, **kwargs):
# #     instance = self.get_object()
# #     instance.deleted_at = timezone.now()
# #     instance.user_deleted = request.user
# #     instance.save()
# #     return Response(
# #         {"detail": "AffiliationAVC04 deleted successfully"},
# #         status=status.HTTP_204_NO_CONTENT,
# #     )
# #
# # def get_queryset(self):
# #     if self.request.query_params.get("show_deleted") == "true":
# #         return Grade.objects.all()
# #     return Grade.objects.filter(deleted_at__isnull=True)
