#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from django.db import models

from django.utils import timezone
from police_personnel.models import Personnel
from users.models import CustomUser


# Create your models here.
class FilePersonnel(models.Model):

    has_file = models.BooleanField(default=False, verbose_name="has file")
    personnel = models.ForeignKey(
        Personnel,
        on_delete=models.SET_NULL,
        null=True,
        related_name="file_personnel",
        verbose_name="personnel",
    )
    documents_has = models.TextField(
        null=True, blank=True, verbose_name="documents has"
    )
    observation = models.TextField(null=True, blank=True, verbose_name="observation")

    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    user_created = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="file_created",
        verbose_name="User Created",
    )
    user_updated = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="file_updated",
        verbose_name="User Updated",
    )
    user_deleted = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="file_deleted",
        verbose_name="User Deleted",
    )

    class Meta:
        db_table = "file_personnel"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.documents_has}"
