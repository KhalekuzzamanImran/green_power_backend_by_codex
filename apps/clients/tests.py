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
            name="Client One",
            code="CLIENT_ONE",
            client_type=self.client_type,
            dashboard_scope=self.scope,
        )
        self.client_two = Client.objects.create(
            name="Client Two",
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

# Create your tests here.
