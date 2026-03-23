from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class ClientProfile(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="client_profile")
    client = models.ForeignKey("clients.Client", on_delete=models.CASCADE, related_name="client_users")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user"], name="unique_client_profile_user"),
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.client.name}"


class OMClientAccess(BaseModel):
    om_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assigned_clients")
    client = models.ForeignKey("clients.Client", on_delete=models.CASCADE, related_name="assigned_om_users")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["om_user", "client"], name="unique_om_client_access"),
        ]
        verbose_name_plural = "O&M client access"

    def __str__(self):
        return f"{self.om_user.username} -> {self.client.name}"


class ClientDashboardAccess(BaseModel):
    client_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dashboard_accesses")
    dashboard = models.ForeignKey("dashboards.Dashboard", on_delete=models.CASCADE, related_name="allowed_users")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["client_user", "dashboard"], name="unique_client_dashboard_access"),
        ]

    def __str__(self):
        return f"{self.client_user.username} -> {self.dashboard.code}"


class UserPermissionOverride(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="permission_override")
    can_set_threshold = models.BooleanField(default=False)
    can_view_all_clients = models.BooleanField(default=False)

    def __str__(self):
        return f"Overrides for {self.user.username}"

# Create your models here.
