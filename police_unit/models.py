#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from django.db import models

from users.models import CustomUser


# Create your models here.
class Units(models.Model):
    name = models.CharField(max_length=250, verbose_name="Unit Name")

    commander = models.ForeignKey(
        "police_personnel.Personnel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="commanded_unit",
        verbose_name="Commander",
    )

    assistant = models.ManyToManyField(
        "police_personnel.Personnel",
        # null=True,
        blank=True,
        related_name="assistant_units",
        verbose_name="Assistant",
    )

    created_at = models.DateTimeField(
        null=True, auto_now_add=True, verbose_name="Created At"
    )
    updated_at = models.DateTimeField(
        auto_now=True, null=True, blank=True, verbose_name="Modified At"
    )
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Deleted At")

    user_created = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="policeunit_created",
        verbose_name="User Created",
    )
    user_updated = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="policeunit_modified",
        verbose_name="User Update",
    )
    user_deleted = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="policeunit_deleted",
        verbose_name="User Deleted",
    )

    class Meta:
        db_table = "police_unit"
        verbose_name = "Police Unit"
        verbose_name_plural = "Police Units"

    def __str__(self):
        return f"{self.name} - {self.commander}"
