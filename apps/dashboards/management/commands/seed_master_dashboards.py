from django.core.management.base import BaseCommand

from apps.dashboards.models import Dashboard, DashboardType


MASTER_DASHBOARDS = [
    ("Grid-Tied Main", "GRID_TIED_MAIN", DashboardType.GRID_TIED_MAIN),
    ("Grid-Tied Management", "GRID_TIED_MANAGEMENT", DashboardType.GRID_TIED_MANAGEMENT),
    ("Apartment Main", "APARTMENT_MAIN", DashboardType.APARTMENT_MAIN),
    ("Apartment Floor Wise", "APARTMENT_FLOOR_WISE", DashboardType.APARTMENT_FLOOR_WISE),
    ("Industry Main", "INDUSTRY_MAIN", DashboardType.INDUSTRY_MAIN),
    ("Industry Zoning", "INDUSTRY_ZONING", DashboardType.INDUSTRY_ZONING),
    ("Industry Board", "INDUSTRY_BOARD", DashboardType.INDUSTRY_BOARD),
    ("Industry MD/CEO", "INDUSTRY_MD_CEO", DashboardType.INDUSTRY_MD_CEO),
    ("Industry Owner", "INDUSTRY_OWNER", DashboardType.INDUSTRY_OWNER),
]


class Command(BaseCommand):
    help = "Seed the master dashboard catalog."

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for name, code, dashboard_type in MASTER_DASHBOARDS:
            _, created = Dashboard.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "dashboard_type": dashboard_type,
                    "is_active": True,
                },
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Dashboard seed complete. created={created_count} updated={updated_count}"
            )
        )
