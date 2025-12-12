#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from django.db import models
from django.utils import timezone

from hospital.models import Hospital
from police_personnel.models import Personnel
from users.models import CustomUser


# Create your models here.
class AffiliationAVC09(models.Model):
    # original_file = models.FileField(upload_to="documents/%Y/%m/%d/")
    personnel = models.ForeignKey(
        Personnel, on_delete=models.SET_NULL, null=True, verbose_name="personel"
    )
    insured_number = models.CharField(max_length=128, verbose_name="insured number")
    employer_number = models.CharField(max_length=128, verbose_name="employer number")
    type_risk = models.CharField(max_length=255, verbose_name="type of risk")
    isue_date = models.DateField(verbose_name="isue date")
    from_date = models.DateField(verbose_name="from date")
    to_date = models.DateField(verbose_name="until date")
    days_incapacity = models.CharField(
        max_length=10, blank=True, verbose_name="days incapacity"
    )

    hospital = models.ForeignKey(
        Hospital, on_delete=models.SET_NULL, null=True, verbose_name="hospital"
    )

    matricula = models.CharField(
        null=True, blank=True, max_length=128, verbose_name="insured number"
    )

    state = models.CharField(
        null=True, blank=True, max_length=128, verbose_name="insured number"
    )

    delivery_date = models.DateTimeField(
        null=True, blank=True, verbose_name="delivery date"
    )

    created_at = models.DateTimeField(
        null=True, auto_now_add=True, verbose_name="Created At"
    )
    modified_at = models.DateTimeField(
        auto_now=True, null=True, blank=True, verbose_name="Modified At"
    )
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Deleted At")

    user_created = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="affiliationavc09_created",
        verbose_name="User Created",
    )
    user_modified = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="affiliationavc09_modified",
        verbose_name="User Modified",
    )
    user_deleted = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="affiliationavc09_deleted",
        verbose_name="User Deleted",
    )

    def sof_delete(self, user=None):
        self.deleted_at = timezone.now()
        if user:
            self.user_deleted = user

        self.save()

    class Meta:
        db_table = "affiliationsavc09"
        ordering = ["-created_at"]
        verbose_name = "Affiliation AVC09"
        verbose_name_plural = "Affiliations AVC09"

    def __str__(self):
        return f"Documento de {self.last_name or 'Pendiente'} - ID: {self.id}"
