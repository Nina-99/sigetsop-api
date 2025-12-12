#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Group,
    Permission,
    PermissionsMixin,
)
from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="role name")
    description = models.TextField(blank=True, verbose_name="description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    user_created = models.ForeignKey(
        "CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        related_name="roles_created",
        verbose_name="user created",
    )
    user_updated = models.ForeignKey(
        "CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        related_name="roles_updated",
        verbose_name="user updated",
    )
    user_deleted = models.ForeignKey(
        "CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        related_name="roles_deleted",
        verbose_name="user deleted",
    )

    class Meta:
        db_table = "role"

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=128, verbose_name="first name")
    last_name = models.CharField(max_length=128, verbose_name="last name")
    maternal_name = models.CharField(
        max_length=128, blank=True, verbose_name="maternal name"
    )
    username = models.CharField(max_length=128, unique=True, verbose_name="username")
    email = models.EmailField(unique=True, verbose_name="email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="phone")
    role = models.ForeignKey(
        Role, on_delete=models.SET_NULL, null=True, verbose_name="role"
    )
    is_active = models.BooleanField(default=True, verbose_name="is active")
    is_staff = models.BooleanField(default=False, verbose_name="is staff")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="updated at")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="deleted at")

    user_created = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        related_name="users_created",
        verbose_name="user created",
    )
    user_updated = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        related_name="users_updated",
        verbose_name="user updated",
    )
    user_deleted = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        related_name="users_deleted",
        verbose_name="user deleted",
    )

    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name="customuser_set",
        verbose_name="groups",
        help_text="The groups this user belongs to.",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="customuser_set",
        verbose_name="user permissions",
        help_text="Specific permissions for this user.",
    )

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        db_table = "users"

    def save(self, *args, **kwargs):
        if self.first_name:
            self.first_name = self.first_name.upper()
        if self.last_name:
            self.last_name = self.last_name.upper()
        if self.maternal_name:
            self.maternal_name = self.maternal_name.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
