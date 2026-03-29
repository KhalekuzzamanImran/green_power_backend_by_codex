from django.core.management.base import BaseCommand

from apps.clients.models import ClientType
from apps.dashboards.models import Dashboard, DashboardScope


MASTER_DASHBOARDS = [
    ("Grid-Tied Main", "GRID_TIED_MAIN", "GRID_TIED", "MAIN"),
    ("Grid-Tied Management", "GRID_TIED_MANAGEMENT", "GRID_TIED", "MANAGEMENT"),
    ("Apartment Main", "APARTMENT_MAIN", "APARTMENT", "MAIN"),
    ("Apartment Floor Wise", "APARTMENT_FLOOR_WISE", "APARTMENT", "FLOOR_WISE"),
    ("Industry Main", "INDUSTRY_MAIN", "INDUSTRY", "MAIN"),
    ("Industry Zoning", "INDUSTRY_ZONING", "INDUSTRY", "ZONING"),
    ("Industry Board", "INDUSTRY_BOARD", "INDUSTRY", "BOARD"),
    ("Industry MD/CEO", "INDUSTRY_MD_CEO", "INDUSTRY", "MD_CEO"),
    ("Industry Owner", "INDUSTRY_OWNER", "INDUSTRY", "OWNER"),
]

MASTER_CLIENT_TYPES = [
    ("GRID_TIED", "Grid-Tied"),
    ("APARTMENT", "Apartment"),
    ("INDUSTRY", "Industry"),
]

MASTER_SCOPES = [
    ("MAIN", "Main Dashboard"),
    ("MANAGEMENT", "Management Dashboard"),
    ("FLOOR_WISE", "Floor-wise Dashboard"),
    ("ZONING", "Zoning Dashboard"),
    ("BOARD", "Board Dashboard"),
    ("MD_CEO", "MD / CEO Dashboard"),
    ("OWNER", "Owner Dashboard"),
]


class Command(BaseCommand):
    help = "Seed the master dashboard catalog."

    def handle(self, *args, **options):
        client_types = {}
        scopes = {}
        for code, name in MASTER_CLIENT_TYPES:
            client_type, _ = ClientType.objects.update_or_create(
                code=code,
                defaults={"name": name, "is_active": True},
            )
            client_types[code] = client_type

        for code, name in MASTER_SCOPES:
            scope, _ = DashboardScope.objects.update_or_create(
                code=code,
                defaults={"name": name, "is_active": True},
            )
            scopes[code] = scope

        created_count = 0
        updated_count = 0

        for name, code, client_type_code, scope_code in MASTER_DASHBOARDS:
            _, created = Dashboard.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "client_type": client_types[client_type_code],
                    "scope": scopes[scope_code],
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
