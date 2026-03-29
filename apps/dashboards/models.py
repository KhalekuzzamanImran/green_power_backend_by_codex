from django.db import models

from apps.core.models import BaseModel
from apps.clients.models import ClientType


class DashboardScope(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Dashboard(BaseModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100, unique=True)
    client_type = models.ForeignKey(ClientType, on_delete=models.PROTECT, related_name="dashboards")
    scope = models.ForeignKey(DashboardScope, on_delete=models.PROTECT, related_name="dashboards")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["client_type", "scope"], name="unique_dashboard_client_type_scope"),
        ]

    def __str__(self):
        return self.name
