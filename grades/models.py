#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from django.db import models
from rest_framework.fields import timezone

from users.models import CustomUser


class Grade(models.Model):
    grade = models.CharField(max_length=100, unique=True, verbose_name="grade")
    grade_abbr = models.CharField(
        max_length=50, unique=True, verbose_name="grade abbreviation"
    )
    created_at = models.DateTimeField(null=True, auto_now_add=True, verbose_name="created at")
    updated_at = models.DateTimeField(null=True, auto_now=True, verbose_name="updated at")
    deleted_at = models.DateTimeField(null=True, auto_now_add=True, verbose_name="deleted at")

    user_created = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="grades_created",
        verbose_name="user created",
    )
    user_updated = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="grades_updated",
        verbose_name="user updated",
    )
    user_deleted = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="grades_deleted",
        verbose_name="user deleted",
    )

    def __str__(self):
        return f"{self.grade} ({self.grade_abbr})"

    def sof_delete(self, user=None):
        self.deleted_at = timezone.now()
        if user:
            self.user_deleted = user

        self.save()

    class Meta:
        db_table = "grade"
        ordering = ["grade"]
