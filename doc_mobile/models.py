from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()


class DocMobile(models.Model):
    file = models.FileField(upload_to="avc09_uploads/", verbose_name="Documento subido")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Usuario de la sesión"
    )
    session_id = models.CharField(max_length=255, verbose_name="ID de Sesión WS")
    initial_points = models.TextField(
        null=True, blank=True, verbose_name="Puntos de corrección iniciales (JSON)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AVC09 Upload {self.pk} by {self.user}"

    class Meta:
        verbose_name = "Afiliación AVC09"
        verbose_name_plural = "Afiliaciones AVC09"
