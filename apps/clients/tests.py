from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.access_control.models import OMClientAccess
from apps.accounts.models import RoleChoices, User
from apps.clients.forms import ClientAdminForm
from apps.clients.models import Client, ClientType
from apps.dashboards.models import Dashboard, DashboardScope
from apps.devices.models import Device, DeviceType


class ClientAccessTests(APITestCase):
    def setUp(self):
        self.om_user = User.objects.create_user(
            username="om_user",
            password="testpass123",
            email="om@example.com",
            role=RoleChoices.OM,
        )
        self.client_type, _ = ClientType.objects.get_or_create(code="GRID_TIED", defaults={"name": "Grid-Tied"})
        self.scope, _ = DashboardScope.objects.get_or_create(code="MAIN", defaults={"name": "Main Dashboard"})
        self.client_allowed = Client.objects.create(
            site_name="Allowed Client",
            code="ALLOWED",
            client_type=self.client_type,
            dashboard_scope=self.scope,
        )
        self.client_blocked = Client.objects.create(
            site_name="Blocked Client",
            code="BLOCKED",
            client_type=self.client_type,
            dashboard_scope=self.scope,
        )
        OMClientAccess.objects.create(om_user=self.om_user, client=self.client_allowed)
        refresh = RefreshToken.for_user(self.om_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_om_only_sees_assigned_clients(self):
        response = self.client.get("/api/v1/clients/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_codes = {row["code"] for row in response.data}
        self.assertEqual(returned_codes, {"ALLOWED"})


class ClientSelfEndpointTests(APITestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            username="client_self",
            password="testpass123",
            email="client-self@example.com",
            role=RoleChoices.CLIENT,
        )
        self.client_type, _ = ClientType.objects.get_or_create(code="GRID_TIED", defaults={"name": "Grid-Tied"})
        self.scope, _ = DashboardScope.objects.get_or_create(code="MANAGEMENT", defaults={"name": "Management Dashboard"})
        self.client_obj = Client.objects.create(
            site_name="Self Client",
            code="SELF_CLIENT",
            client_type=self.client_type,
            dashboard_scope=self.scope,
        )
        from apps.access_control.models import UserClientAccess
        UserClientAccess.objects.create(user=self.client_user, client=self.client_obj)
        refresh = RefreshToken.for_user(self.client_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_client_can_fetch_own_client_record(self):
        response = self.client.get("/api/v1/clients/my/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], "SELF_CLIENT")
        self.assertEqual(response.data["client_type_code"], "GRID_TIED")
        self.assertEqual(response.data["dashboard_scope_code"], "MANAGEMENT")


class MultiClientSelectionTests(APITestCase):
    def setUp(self):
        from apps.access_control.models import UserClientAccess

        self.client_user = User.objects.create_user(
            username="multi_client_user",
            password="testpass123",
            email="multi-client@example.com",
            role=RoleChoices.CLIENT,
        )
        self.client_type, _ = ClientType.objects.get_or_create(code="GRID_TIED", defaults={"name": "Grid-Tied"})
        self.scope, _ = DashboardScope.objects.get_or_create(code="MAIN", defaults={"name": "Main Dashboard"})
        self.client_one = Client.objects.create(
            site_name="Client One",
            code="CLIENT_ONE",
            client_type=self.client_type,
            dashboard_scope=self.scope,
        )
        self.client_two = Client.objects.create(
            site_name="Client Two",
            code="CLIENT_TWO",
            client_type=self.client_type,
            dashboard_scope=self.scope,
        )
        UserClientAccess.objects.create(user=self.client_user, client=self.client_one)
        UserClientAccess.objects.create(user=self.client_user, client=self.client_two)
        refresh = RefreshToken.for_user(self.client_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_client_can_list_accessible_clients_for_selection(self):
        response = self.client.get("/api/v1/clients/my-clients/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_codes = {row["code"] for row in response.data}
        self.assertEqual(returned_codes, {"CLIENT_ONE", "CLIENT_TWO"})

    def test_client_must_select_client_when_multiple_clients_exist(self):
        response = self.client.get("/api/v1/clients/my/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("client_id", response.data)

    def test_client_can_fetch_selected_client_context(self):
        response = self.client.get(f"/api/v1/clients/my/?client_id={self.client_two.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], "CLIENT_TWO")


class ClientScopeValidationTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="client_admin_user",
            password="testpass123",
            email="client-admin-user@example.com",
            role=RoleChoices.ADMIN,
        )
        self.grid_type, _ = ClientType.objects.get_or_create(code="GRID_TIED", defaults={"name": "Grid-Tied"})
        self.industry_type, _ = ClientType.objects.get_or_create(code="INDUSTRY", defaults={"name": "Industry"})
        self.main_scope, _ = DashboardScope.objects.get_or_create(code="MAIN", defaults={"name": "Main Dashboard"})
        self.management_scope, _ = DashboardScope.objects.get_or_create(
            code="MANAGEMENT",
            defaults={"name": "Management Dashboard"},
        )
        self.board_scope, _ = DashboardScope.objects.get_or_create(code="BOARD", defaults={"name": "Board Dashboard"})
        Dashboard.objects.get_or_create(
            code="GRID_TIED_MAIN",
            defaults={
                "name": "Grid-Tied Main",
                "client_type": self.grid_type,
                "scope": self.main_scope,
            },
        )
        Dashboard.objects.get_or_create(
            code="GRID_TIED_MANAGEMENT",
            defaults={
                "name": "Grid-Tied Management",
                "client_type": self.grid_type,
                "scope": self.management_scope,
            },
        )
        Dashboard.objects.get_or_create(
            code="INDUSTRY_BOARD",
            defaults={
                "name": "Industry Board",
                "client_type": self.industry_type,
                "scope": self.board_scope,
            },
        )
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_api_rejects_scope_not_available_for_selected_client_type(self):
        response = self.client.post(
            "/api/v1/clients/",
            {
                "site_name": "Invalid Grid Site",
                "code": "INVALID_GRID_SITE",
                "client_type": str(self.grid_type.id),
                "dashboard_scope": str(self.board_scope.id),
                "address": "Dhaka",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("dashboard_scope", response.data)


class ClientAdminScopeFilteringTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="django_admin",
            password="testpass123",
            email="django-admin@example.com",
            role=RoleChoices.ADMIN,
            is_staff=True,
            is_superuser=True,
        )
        self.grid_type, _ = ClientType.objects.get_or_create(code="GRID_TIED", defaults={"name": "Grid-Tied"})
        self.industry_type, _ = ClientType.objects.get_or_create(code="INDUSTRY", defaults={"name": "Industry"})
        self.main_scope, _ = DashboardScope.objects.get_or_create(code="MAIN", defaults={"name": "Main Dashboard"})
        self.management_scope, _ = DashboardScope.objects.get_or_create(
            code="MANAGEMENT",
            defaults={"name": "Management Dashboard"},
        )
        self.board_scope, _ = DashboardScope.objects.get_or_create(code="BOARD", defaults={"name": "Board Dashboard"})
        Dashboard.objects.get_or_create(
            code="GRID_TIED_MAIN",
            defaults={
                "name": "Grid-Tied Main",
                "client_type": self.grid_type,
                "scope": self.main_scope,
            },
        )
        Dashboard.objects.get_or_create(
            code="GRID_TIED_MANAGEMENT",
            defaults={
                "name": "Grid-Tied Management",
                "client_type": self.grid_type,
                "scope": self.management_scope,
            },
        )
        Dashboard.objects.get_or_create(
            code="INDUSTRY_BOARD",
            defaults={
                "name": "Industry Board",
                "client_type": self.industry_type,
                "scope": self.board_scope,
            },
        )

    def test_admin_form_limits_dashboard_scopes_by_selected_client_type(self):
        form = ClientAdminForm(data={"client_type": str(self.grid_type.id)})

        returned_codes = set(form.fields["dashboard_scope"].queryset.values_list("code", flat=True))
        self.assertEqual(returned_codes, {"MAIN", "MANAGEMENT"})

    def test_admin_scope_options_endpoint_returns_only_matching_scopes(self):
        self.client.login(username="django_admin", password="testpass123")

        response = self.client.get(
            reverse("hardened_admin:clients_client_dashboard_scope_options"),
            {"client_type_id": str(self.grid_type.id)},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_names = {item["name"] for item in response.json()["results"]}
        self.assertEqual(returned_names, {"Main Dashboard", "Management Dashboard"})

    def test_client_change_page_shows_installed_devices_inline(self):
        client = Client.objects.create(
            site_name="Client With Devices",
            code="CLIENT_WITH_DEVICES",
            client_type=self.grid_type,
            dashboard_scope=self.main_scope,
        )
        Device.objects.create(
            client=client,
            name="Grid Alpha Inverter",
            serial_number="GRID-ALPHA-INV-001",
            device_type=DeviceType.SOLAR,
        )
        Device.objects.create(
            client=client,
            name="Grid Alpha BESS",
            serial_number="GRID-ALPHA-BESS-001",
            device_type=DeviceType.BESS,
        )

        self.client.login(username="django_admin", password="testpass123")
        response = self.client.get(reverse("hardened_admin:clients_client_change", args=[client.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Installed devices")
        self.assertContains(response, "GRID-ALPHA-INV-001")
        self.assertContains(response, "GRID-ALPHA-BESS-001")
