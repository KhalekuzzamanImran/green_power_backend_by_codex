from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import RoleChoices, User
from apps.clients.models import ClientType
from apps.dashboards.models import Dashboard, DashboardScope


class DashboardLookupTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="lookup_admin",
            password="testpass123",
            email="lookup-admin@example.com",
            role=RoleChoices.ADMIN,
        )
        ClientType.objects.get_or_create(code="GRID_TIED", defaults={"name": "Grid-Tied"})
        ClientType.objects.get_or_create(code="INDUSTRY", defaults={"name": "Industry"})
        DashboardScope.objects.get_or_create(code="MAIN", defaults={"name": "Main Dashboard"})
        DashboardScope.objects.get_or_create(code="BOARD", defaults={"name": "Board Dashboard"})
        self.grid_type = ClientType.objects.get(code="GRID_TIED")
        self.industry_type = ClientType.objects.get(code="INDUSTRY")
        self.main_scope = DashboardScope.objects.get(code="MAIN")
        self.board_scope = DashboardScope.objects.get(code="BOARD")
        Dashboard.objects.get_or_create(
            code="GRID_TIED_MAIN",
            defaults={
                "name": "Grid-Tied Main",
                "client_type": self.grid_type,
                "scope": self.main_scope,
                "is_active": True,
            },
        )
        Dashboard.objects.get_or_create(
            code="INDUSTRY_BOARD",
            defaults={
                "name": "Industry Board",
                "client_type": self.industry_type,
                "scope": self.board_scope,
                "is_active": True,
            },
        )
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_client_type_lookup_endpoint(self):
        response = self.client.get("/api/v1/client-types/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        codes = {row["code"] for row in response.data}
        self.assertTrue({"GRID_TIED", "INDUSTRY"}.issubset(codes))

    def test_dashboard_scope_lookup_endpoint(self):
        response = self.client.get("/api/v1/dashboard-scopes/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        codes = {row["code"] for row in response.data}
        self.assertTrue({"MAIN", "BOARD"}.issubset(codes))

    def test_dashboard_list_supports_client_type_and_scope_filters(self):
        response = self.client.get("/api/v1/dashboards/?client_type=GRID_TIED&scope=MAIN")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        codes = [row["code"] for row in response.data]
        self.assertEqual(codes, ["GRID_TIED_MAIN"])
