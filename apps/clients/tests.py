from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.access_control.models import OMClientAccess
from apps.accounts.models import RoleChoices, User
from apps.clients.models import Client
from apps.dashboards.models import ClientType, DashboardScope


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
            name="Allowed Client",
            code="ALLOWED",
            client_type=self.client_type,
            dashboard_scope=self.scope,
        )
        self.client_blocked = Client.objects.create(
            name="Blocked Client",
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
            name="Self Client",
            code="SELF_CLIENT",
            client_type=self.client_type,
            dashboard_scope=self.scope,
        )
        from apps.access_control.models import ClientProfile
        ClientProfile.objects.create(user=self.client_user, client=self.client_obj)
        refresh = RefreshToken.for_user(self.client_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_client_can_fetch_own_client_record(self):
        response = self.client.get("/api/v1/clients/my/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], "SELF_CLIENT")
        self.assertEqual(response.data["client_type_code"], "GRID_TIED")
        self.assertEqual(response.data["dashboard_scope_code"], "MANAGEMENT")

# Create your tests here.
