from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()


class DocMobile(models.Model):
    # 1. Campo 'file' (Archivo): Necesario para guardar el documento subido.
    file = models.FileField(upload_to="avc09_uploads/", verbose_name="Documento subido")

    # 2. Campo 'user' (Usuario): Necesario si la subida está asociada al usuario autenticado.
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Usuario de la sesión"
    )

    # 3. Campo 'session_id' (ID de Sesión): Necesario para saber a qué WebSocket notificar.
    session_id = models.CharField(max_length=255, verbose_name="ID de Sesión WS")

    # 4. Campo de Puntos Iniciales (Opcional, si quieres persistirlos en el modelo)
    # Si los puntos son JSON, puedes usar JSONField (Django >= 3.1 con PostgreSQL)
    # o CharField/TextField si usas otra DB y JSON.stringify
    initial_points = models.TextField(
        null=True, blank=True, verbose_name="Puntos de corrección iniciales (JSON)"
    )

    # ... otros campos de fecha, estado, etc.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AVC09 Upload {self.pk} by {self.user}"

    class Meta:
        verbose_name = "Afiliación AVC09"
        verbose_name_plural = "Afiliaciones AVC09"
