from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class AuditAction(models.TextChoices):
    CREATE = "CREATE", "Create"
    UPDATE = "UPDATE", "Update"
    DELETE = "DELETE", "Delete"
    ASSIGN = "ASSIGN", "Assign"
    THRESHOLD_UPDATE = "THRESHOLD_UPDATE", "Threshold Update"
    LOGIN = "LOGIN", "Login"


class AuditLog(BaseModel):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=30, choices=AuditAction.choices)
    target_type = models.CharField(max_length=100)
    target_id = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} {self.target_type}:{self.target_id}"

# Create your models here.
