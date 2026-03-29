from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import BaseModel


class ClientType(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        db_table = "dashboards_clienttype"

    def __str__(self):
        return self.name


class Client(BaseModel):
    site_name = models.CharField(max_length=255, verbose_name="Company / Site Name")
    code = models.CharField(max_length=100, unique=True)
    client_type = models.ForeignKey("clients.ClientType", on_delete=models.PROTECT, related_name="clients")
    dashboard_scope = models.ForeignKey("dashboards.DashboardScope", on_delete=models.PROTECT, related_name="clients")
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["site_name"]

    def clean(self):
        super().clean()
        from apps.dashboards.models import Dashboard

        if self.client_type_id and self.dashboard_scope_id and not Dashboard.objects.filter(
            client_type_id=self.client_type_id,
            scope_id=self.dashboard_scope_id,
            is_active=True,
        ).exists():
            raise ValidationError({"dashboard_scope": "Selected dashboard scope is not available for this client type."})

    def __str__(self):
        return self.site_name
