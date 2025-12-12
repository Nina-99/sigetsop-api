#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from re import VERBOSE
from django.db import models
from django.utils import timezone

from grades.models import Grade
from users.models import CustomUser

from .managers import PersonnelManager


# Create your models here.
class Personnel(models.Model):
    grade = models.ForeignKey(
        Grade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="officers",
        verbose_name="grade",
    )

    last_name = models.CharField(max_length=128, blank=True, verbose_name="last name")
    maternal_name = models.CharField(
        max_length=128, blank=True, verbose_name="maternal name"
    )
    first_name = models.CharField(max_length=128, blank=True, verbose_name="first name")
    middle_name = models.CharField(
        null=True, max_length=128, blank=True, verbose_name="middle name"
    )
    identity_card = models.CharField(
        null=True, max_length=20, unique=True, verbose_name="identity card"
    )
    birthdate = models.DateField(null=True, verbose_name="birthdate")
    genre = models.CharField(null=True, max_length=20, blank=True, verbose_name="genre")
    phone = models.CharField(null=True, max_length=20, blank=True, verbose_name="phone")
    joining_police = models.DateField(null=True, verbose_name="joining police")
    scale = models.CharField(null=True, max_length=50, verbose_name="scale")
    insured_number = models.CharField(
        null=True, max_length=128, verbose_name="insured number"
    )
    employer_number = models.CharField(
        null=True, max_length=128, verbose_name="employer number"
    )
    company_name = models.CharField(max_length=128, verbose_name="company name")
    current_destination = models.ForeignKey(
        "police_unit.Units",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
        verbose_name="units",
    )
    address = models.CharField(max_length=255, verbose_name="address")
    door_number = models.CharField(
        max_length=10, blank=True, verbose_name="door number"
    )
    area = models.CharField(null=True, max_length=100, verbose_name="area")
    reference = models.CharField(
        null=True, blank=True, max_length=100, verbose_name="reference"
    )
    reference_phone = models.CharField(
        max_length=20, blank=True, verbose_name="reference phone"
    )

    is_active = models.BooleanField(default=True, verbose_name="is active")
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    user_created = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="officers_created",
        verbose_name="user created",
    )
    user_updated = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="officers_updated",
        verbose_name="user updated",
    )
    user_deleted = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="officers_deleted",
        verbose_name="user deleted",
    )

    objects = PersonnelManager

    class Meta:
        db_table = "police_personnel"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def sof_delete(self, using=None, keep_parents=False, user=None):
        self.is_active = False
        self.deleted_at = timezone.now()
        if user:
            self.user_deleted = user

        self.save()

    def save(self, *args, **kwargs):
        if self.first_name:
            self.first_name = self.first_name.upper()
        if self.middle_name:
            self.middle_name = self.middle_name.upper()
        if self.last_name:
            self.last_name = self.last_name.upper()
        if self.maternal_name:
            self.maternal_name = self.maternal_name.upper()
        if self.company_name:
            self.company_name = self.company_name.upper()
        super().save(*args, **kwargs)
