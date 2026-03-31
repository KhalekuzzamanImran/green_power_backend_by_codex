from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import BaseModel


class RoleChoices(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    OM = "OM", "O&M"
    CLIENT = "CLIENT", "Client"


class User(BaseModel, AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=RoleChoices.choices)
    phone = models.CharField(max_length=20, blank=True)

    REQUIRED_FIELDS = ["email", "role"]

    class Meta:
        db_table = "users"
        ordering = ["username"]
        indexes = [
            models.Index(fields=["role", "is_active"], name="user_role_active_idx"),
            models.Index(fields=["first_name"], name="user_first_name_idx"),
            models.Index(fields=["last_name"], name="user_last_name_idx"),
        ]

    def __str__(self):
        return f"{self.username} ({self.role})"
