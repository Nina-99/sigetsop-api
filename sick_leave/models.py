#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from django.db import models

from hospital.models import Hospital
from police_personnel.models import Personnel
from users.models import CustomUser


# Create your models here.
class SickLeave(models.Model):
    personnel = models.ForeignKey(
        Personnel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sickleave_personnel",
        verbose_name="police personnel",
    )
    classification = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sickleave_hospital",
        verbose_name="hospital",
    )
    brought_by = models.CharField(max_length=150)
    status = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    modified_at = models.DateTimeField(
        auto_now=True, null=True, blank=True, verbose_name="Modified At"
    )
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Deleted At")

    user_created = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sickleave_created",
        verbose_name="User Created",
    )
    user_modified = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sickleave_modified",
        verbose_name="User Modified",
    )
    user_deleted = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sickleave_deleted",
        verbose_name="User Deleted",
    )

    class Meta:
        db_table = "bajas"
        verbose_name = "Sick Leave"
        verbose_name_plural = "Sick Leaves"

    def __str__(self):
        return (
            f"{self.classification} - {self.start_date} to {self.end_date or 'ongoing'}"
        )
