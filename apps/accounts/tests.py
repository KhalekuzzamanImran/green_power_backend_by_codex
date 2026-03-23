from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import RoleChoices, User
from apps.clients.models import Client
from apps.access_control.models import ClientProfile, ClientDashboardAccess
from apps.dashboards.models import Dashboard, DashboardType


class MeEndpointTests(APITestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            username="client_user",
            password="testpass123",
            email="client@example.com",
            role=RoleChoices.CLIENT,
        )
        self.client_obj = Client.objects.create(name="Client A", code="CLIENT_A")
        ClientProfile.objects.create(user=self.client_user, client=self.client_obj)
        self.dashboard = Dashboard.objects.create(
            name="Grid Management",
            code="GRID_TIED_MANAGEMENT",
            dashboard_type=DashboardType.GRID_TIED_MANAGEMENT,
        )
        ClientDashboardAccess.objects.create(client_user=self.client_user, dashboard=self.dashboard)
        refresh = RefreshToken.for_user(self.client_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_me_returns_client_bootstrap_payload(self):
        response = self.client.get("/api/v1/auth/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role"], RoleChoices.CLIENT)
        self.assertEqual(response.data["client_id"], str(self.client_obj.id))
        self.assertEqual(response.data["allowed_dashboards"], ["GRID_TIED_MANAGEMENT"])

# Create your tests here.
