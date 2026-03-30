from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import BaseModel
from apps.clients.utils import generate_unique_client_code, normalize_client_code


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

        if self.code:
            self.code = normalize_client_code(self.code)
            duplicate_qs = Client.objects.filter(code=self.code)
            if self.pk:
                duplicate_qs = duplicate_qs.exclude(pk=self.pk)
            if duplicate_qs.exists():
                raise ValidationError({"code": "Client code must be unique."})

        if self.client_type_id and self.dashboard_scope_id and not Dashboard.objects.filter(
            client_type_id=self.client_type_id,
            scope_id=self.dashboard_scope_id,
            is_active=True,
        ).exists():
            raise ValidationError({"dashboard_scope": "Selected dashboard scope is not available for this client type."})

    def save(self, *args, **kwargs):
        if self.code:
            self.code = normalize_client_code(self.code)
        else:
            self.code = generate_unique_client_code(self.site_name, model=type(self), exclude_client_id=self.pk)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.site_name
