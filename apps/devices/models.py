from django.db import models

from apps.core.models import BaseModel


class DeviceType(models.TextChoices):
    DG = "DG", "DG"
    SOLAR = "SOLAR", "Solar"
    GRID = "GRID", "Grid"
    BESS = "BESS", "BESS"


class Device(BaseModel):
    client = models.ForeignKey("clients.Client", on_delete=models.CASCADE, related_name="devices")
    name = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=150, unique=True)
    device_type = models.CharField(max_length=20, choices=DeviceType.choices)
    is_active = models.BooleanField(default=True)
    installed_at = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.serial_number})"


class DeviceData(BaseModel):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="data_points")
    payload = models.JSONField()
    recorded_at = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"{self.device.serial_number} @ {self.recorded_at.isoformat()}"

# Create your models here.
