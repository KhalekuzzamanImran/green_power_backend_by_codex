from django.conf import settings
from django.db import models

from common.models import AuditModel


class ServiceZone(AuditModel):
    STATUS_CRITICAL = "critical"
    STATUS_MAJOR = "major"
    STATUS_MINOR = "minor"
    STATUS_CHOICES = [
        (STATUS_CRITICAL, "Critical"),
        (STATUS_MAJOR, "Major"),
        (STATUS_MINOR, "Minor"),
    ]
    NETWORK_ONLINE = "online"
    NETWORK_OFFLINE = "offline"
    NETWORK_WARNING = "warning"
    NETWORK_STATUS_CHOICES = [
        (NETWORK_ONLINE, "Online"),
        (NETWORK_OFFLINE, "Offline"),
        (NETWORK_WARNING, "Warning"),
    ]

    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50, unique=True)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES)
    network_status = models.CharField(max_length=30, choices=NETWORK_STATUS_CHOICES)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="service_zones"
    )

    class Meta:
        db_table = "service_zones"

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class Device(AuditModel):
    device_name = models.CharField(max_length=150)
    device_code = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=30, choices=ServiceZone.STATUS_CHOICES)
    remark = models.TextField(blank=True)
    physical_details = models.TextField(blank=True)
    service_zone = models.ForeignKey(
        ServiceZone, on_delete=models.PROTECT, related_name="devices"
    )

    class Meta:
        db_table = "devices"

    def __str__(self) -> str:
        return f"{self.device_name} ({self.device_code})"


class DeviceStat(AuditModel):
    state = models.CharField(max_length=100)
    device = models.ForeignKey(Device, on_delete=models.PROTECT, related_name="stats")

    class Meta:
        db_table = "device_stats"

    def __str__(self) -> str:
        return f"{self.device.device_code}: {self.state}"
