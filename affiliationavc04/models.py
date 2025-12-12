#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from django.conf import settings
from django.db import models
from django.utils import timezone

from police_personnel.models import Personnel
from users.models import CustomUser


# Create your models here.
class AffiliationAVC04(models.Model):
    # document = models.FileField(
    #     upload_to="affiliations/pdfs/",
    #     null=True,
    #     blank=True,
    #     verbose_name="Document (PDF)",
    # )
    original_file = models.FileField(upload_to="documents/%Y/%m/%d/")
    last_name = models.CharField(max_length=128, blank=True, verbose_name="last name")
    maternal_name = models.CharField(
        max_length=128, blank=True, verbose_name="maternal name"
    )
    first_name = models.CharField(max_length=128, blank=True, verbose_name="first name")
    # middle_name = models.CharField(
    #     max_length=128, blank=True, verbose_name="middle name"
    # )
    insured_number = models.CharField(
        max_length=20, unique=True, verbose_name="insured number"
    )
    birthdate = models.DateField(verbose_name="birthdate")
    genre = models.CharField(max_length=20, blank=True, verbose_name="genre")
    joining_police = models.DateField(verbose_name="joining police")
    insured_number = models.CharField(max_length=128, verbose_name="insured number")
    company_name = models.CharField(max_length=128, verbose_name="company name")
    employer_number = models.CharField(max_length=128, verbose_name="employer number")
    current_destination = models.CharField(
        max_length=128, verbose_name="current destination"
    )
    address = models.CharField(max_length=255, verbose_name="address")
    door_number = models.CharField(
        max_length=10, blank=True, verbose_name="door number"
    )
    area = models.CharField(max_length=100, verbose_name="area")
    location = models.CharField(max_length=100, verbose_name="Location")
    salary = models.CharField(max_length=50, verbose_name="Salary")
    occupation = models.CharField(max_length=100, verbose_name="Occupation")

    date = models.DateField(verbose_name="Date")

    extracted_text = models.TextField(blank=True)
    extraction_date = models.DateTimeField(auto_now_add=True)

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
        related_name="affiliationavc04_created",
        verbose_name="User Created",
    )
    user_modified = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="affiliationavc04_modified",
        verbose_name="User Modified",
    )
    user_deleted = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="affiliationavc04_deleted",
        verbose_name="User Deleted",
    )

    def sof_delete(self, user=None):
        self.deleted_at = timezone.now()
        if user:
            self.user_deleted = user

        self.save()

    class Meta:
        db_table = "affiliationsavc04"
        ordering = ["-created_at"]
        verbose_name = "Affiliation AVC04"
        verbose_name_plural = "Affiliations AVC04"

    def __str__(self):
        return f"Documento de {self.last_name or 'Pendiente'} - ID: {self.id}"
