#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from django.db import models
from django.utils import timezone


class PersonnelQuerySet(models.QuerySet):
    def active(slef):
        return self.filter(delete_at__isnull=True, is_active=True)


class PersonnelManager(models.Manager):
    def get_queryset(self):
        return PersonnelQuerySet(self.model, using=self._db)

    def all_with_deleted(self):
        return super().get_queryset()
