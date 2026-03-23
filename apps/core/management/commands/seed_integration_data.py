from datetime import timedelta
from decimal import Decimal

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.access_control.models import ClientDashboardAccess, ClientProfile, OMClientAccess, UserPermissionOverride
from apps.accounts.models import RoleChoices, User
from apps.clients.models import Client
from apps.dashboards.models import Dashboard
from apps.devices.models import Device, DeviceData, DeviceType
from apps.thresholds.models import DeviceThreshold


class Command(BaseCommand):
    help = "Seed a complete sample RBAC dataset for frontend integration."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default="ChangeMe123!",
            help="Password to use for all seeded users.",
        )

    def handle(self, *args, **options):
        password = options["password"]

        call_command("seed_master_dashboards")

        admin_user = self._upsert_user(
            username="admin_demo",
            email="admin.demo@greenpower.local",
            role=RoleChoices.ADMIN,
            password=password,
            first_name="Admin",
            last_name="Demo",
            phone="01700000001",
            is_staff=True,
            is_superuser=True,
        )
        om_user = self._upsert_user(
            username="om_demo",
            email="om.demo@greenpower.local",
            role=RoleChoices.OM,
            password=password,
            first_name="Operations",
            last_name="Manager",
            phone="01700000002",
        )
        client_management_user = self._upsert_user(
            username="client_grid_management",
            email="client.grid.management@greenpower.local",
            role=RoleChoices.CLIENT,
            password=password,
            first_name="Grid",
            last_name="Manager",
            phone="01700000003",
        )
        client_board_user = self._upsert_user(
            username="client_industry_board",
            email="client.industry.board@greenpower.local",
            role=RoleChoices.CLIENT,
            password=password,
            first_name="Industry",
            last_name="Board",
            phone="01700000004",
        )

        grid_client, _ = Client.objects.update_or_create(
            code="GRID_SITE_ALPHA",
            defaults={
                "name": "Grid Site Alpha",
                "contact_person": "Grid Manager",
                "email": "alpha.client@greenpower.local",
                "phone": "01800000001",
                "address": "Dhaka, Bangladesh",
                "is_active": True,
            },
        )
        industry_client, _ = Client.objects.update_or_create(
            code="INDUSTRY_SITE_BETA",
            defaults={
                "name": "Industry Site Beta",
                "contact_person": "Board Office",
                "email": "beta.client@greenpower.local",
                "phone": "01800000002",
                "address": "Chattogram, Bangladesh",
                "is_active": True,
            },
        )

        ClientProfile.objects.update_or_create(
            user=client_management_user,
            defaults={"client": grid_client},
        )
        ClientProfile.objects.update_or_create(
            user=client_board_user,
            defaults={"client": industry_client},
        )

        OMClientAccess.objects.update_or_create(om_user=om_user, client=grid_client)
        OMClientAccess.objects.update_or_create(om_user=om_user, client=industry_client)

        UserPermissionOverride.objects.update_or_create(
            user=om_user,
            defaults={
                "can_set_threshold": True,
                "can_view_all_clients": False,
            },
        )

        management_dashboard = Dashboard.objects.get(code="GRID_TIED_MANAGEMENT")
        board_dashboard = Dashboard.objects.get(code="INDUSTRY_BOARD")
        ClientDashboardAccess.objects.update_or_create(
            client_user=client_management_user,
            dashboard=management_dashboard,
        )
        ClientDashboardAccess.objects.update_or_create(
            client_user=client_board_user,
            dashboard=board_dashboard,
        )

        grid_device = self._upsert_device(
            client=grid_client,
            name="Grid Alpha Inverter",
            serial_number="GRID-INV-001",
            device_type=DeviceType.SOLAR,
        )
        bess_device = self._upsert_device(
            client=grid_client,
            name="Grid Alpha BESS",
            serial_number="GRID-BESS-001",
            device_type=DeviceType.BESS,
        )
        industry_device = self._upsert_device(
            client=industry_client,
            name="Industry Beta Meter",
            serial_number="IND-GRID-001",
            device_type=DeviceType.GRID,
        )

        self._upsert_threshold(grid_device, "voltage_max", Decimal("230.50"), "V", om_user)
        self._upsert_threshold(bess_device, "temperature_max", Decimal("38.00"), "C", om_user)
        self._upsert_threshold(industry_device, "current_max", Decimal("125.00"), "A", om_user)

        now = timezone.now()
        self._upsert_data_point(
            grid_device,
            recorded_at=now - timedelta(minutes=15),
            payload={"power_kw": 52.3, "voltage": 225.4, "status": "healthy"},
        )
        self._upsert_data_point(
            bess_device,
            recorded_at=now - timedelta(minutes=10),
            payload={"soc": 81.2, "temperature": 32.4, "status": "charging"},
        )
        self._upsert_data_point(
            industry_device,
            recorded_at=now - timedelta(minutes=5),
            payload={"current": 97.5, "frequency": 49.9, "status": "stable"},
        )

        self.stdout.write(self.style.SUCCESS("Integration seed complete."))
        self.stdout.write("Seeded users:")
        self.stdout.write(f"  ADMIN  -> {admin_user.username} / {password}")
        self.stdout.write(f"  O&M    -> {om_user.username} / {password}")
        self.stdout.write(f"  CLIENT -> {client_management_user.username} / {password}")
        self.stdout.write(f"  CLIENT -> {client_board_user.username} / {password}")

    def _upsert_user(self, *, username, email, role, password, first_name, last_name, phone, is_staff=False, is_superuser=False):
        user, _ = User.objects.update_or_create(
            username=username,
            defaults={
                "email": email,
                "role": role,
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "is_active": True,
                "is_staff": is_staff,
                "is_superuser": is_superuser,
            },
        )
        user.set_password(password)
        user.save()
        return user

    def _upsert_device(self, *, client, name, serial_number, device_type):
        device, _ = Device.objects.update_or_create(
            serial_number=serial_number,
            defaults={
                "client": client,
                "name": name,
                "device_type": device_type,
                "is_active": True,
            },
        )
        return device

    def _upsert_threshold(self, device, key, value, unit, updated_by):
        DeviceThreshold.objects.update_or_create(
            device=device,
            key=key,
            defaults={
                "value": value,
                "unit": unit,
                "updated_by": updated_by,
            },
        )

    def _upsert_data_point(self, device, recorded_at, payload):
        DeviceData.objects.update_or_create(
            device=device,
            recorded_at=recorded_at,
            defaults={"payload": payload},
        )
