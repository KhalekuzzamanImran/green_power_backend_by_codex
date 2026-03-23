from django.db import models

from apps.core.models import BaseModel


class DashboardType(models.TextChoices):
    GRID_TIED_MAIN = "GRID_TIED_MAIN", "Grid-Tied Main"
    GRID_TIED_MANAGEMENT = "GRID_TIED_MANAGEMENT", "Grid-Tied Management"
    APARTMENT_MAIN = "APARTMENT_MAIN", "Apartment Main"
    APARTMENT_FLOOR_WISE = "APARTMENT_FLOOR_WISE", "Apartment Floor Wise"
    INDUSTRY_MAIN = "INDUSTRY_MAIN", "Industry Main"
    INDUSTRY_ZONING = "INDUSTRY_ZONING", "Industry Zoning"
    INDUSTRY_BOARD = "INDUSTRY_BOARD", "Industry Board"
    INDUSTRY_MD_CEO = "INDUSTRY_MD_CEO", "Industry MD/CEO"
    INDUSTRY_OWNER = "INDUSTRY_OWNER", "Industry Owner"


class Dashboard(BaseModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100, unique=True)
    dashboard_type = models.CharField(max_length=50, choices=DashboardType.choices)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

# Create your models here.
