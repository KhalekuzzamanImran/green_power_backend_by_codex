from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class DeviceThreshold(BaseModel):
    device = models.ForeignKey("devices.Device", on_delete=models.CASCADE, related_name="thresholds")
    key = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    unit = models.CharField(max_length=20, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["device", "key"], name="unique_device_threshold_key"),
        ]
        ordering = ["key"]

    def __str__(self):
        return f"{self.device.serial_number} {self.key}={self.value}"

# Create your models here.
