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
class AffiliationAVC07(models.Model):
    personnel = models.ForeignKey(
        Personnel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="affiliation_personnel",
        verbose_name="police personnel",
    )
    retirement_date = models.DateField(verbose_name="Retirement Date")
    reason = models.CharField(max_length=100, verbose_name="Reason")
    location = models.CharField(max_length=100, verbose_name="Location")
    salary = models.CharField(max_length=50, verbose_name="Salary")
    occupation = models.CharField(max_length=100, verbose_name="Occupation")
    date = models.DateField(verbose_name="Date")
    status = models.IntegerField(default=1, verbose_name="Status")

    document = models.FileField(
        upload_to="affiliations/pdfs/",
        null=True,
        blank=True,
        verbose_name="Document (PDF)",
    )

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
        related_name="affiliations_created",
        verbose_name="User Created",
    )
    user_modified = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="affiliations_modified",
        verbose_name="User Modified",
    )
    user_deleted = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="affiliations_deleted",
        verbose_name="User Deleted",
    )

    def sof_delete(self, user=None):
        self.deleted_at = timezone.now()
        if user:
            self.user_deleted = user

        self.save()

    class Meta:
        db_table = "affiliationsavc07"
        ordering = ["-created_at"]
        verbose_name = "Affiliation AVC07"
        verbose_name_plural = "Affiliations AVC07"

    def __str__(self):
        return f"Affiliation {self.id} - {self.personnel} ({self.location})"
