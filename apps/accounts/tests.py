from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import RoleChoices, User
from apps.clients.models import Client
from apps.access_control.models import ClientProfile
from apps.dashboards.models import ClientType, Dashboard, DashboardScope


class MeEndpointTests(APITestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            username="client_user",
            password="testpass123",
            email="client@example.com",
            role=RoleChoices.CLIENT,
        )
        self.client_type, _ = ClientType.objects.get_or_create(code="GRID_TIED", defaults={"name": "Grid-Tied"})
        self.scope, _ = DashboardScope.objects.get_or_create(
            code="MANAGEMENT",
            defaults={"name": "Management Dashboard"},
        )
        self.client_obj = Client.objects.create(
            name="Client A",
            code="CLIENT_A",
            client_type=self.client_type,
            dashboard_scope=self.scope,
        )
        ClientProfile.objects.create(user=self.client_user, client=self.client_obj)
        self.dashboard = Dashboard.objects.create(
            name="Grid Management",
            code="GRID_TIED_MANAGEMENT",
            client_type=self.client_type,
            scope=self.scope,
        )
        refresh = RefreshToken.for_user(self.client_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_me_returns_client_bootstrap_payload(self):
        response = self.client.get("/api/v1/auth/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role"], RoleChoices.CLIENT)
        self.assertEqual(response.data["client_id"], str(self.client_obj.id))
        self.assertEqual(response.data["client_type"], "GRID_TIED")
        self.assertEqual(response.data["dashboard_scope"], "MANAGEMENT")
        self.assertEqual(response.data["allowed_dashboards"], ["GRID_TIED_MANAGEMENT"])


class AdminHardeningTests(TestCase):
    def test_client_user_cannot_access_admin_even_if_staff(self):
        User.objects.create_user(
            username="client_admin_blocked",
            password="testpass123",
            email="client-admin-blocked@example.com",
            role=RoleChoices.CLIENT,
            is_staff=True,
        )

        login_response = self.client.post(
            "/admin/login/",
            {"username": "client_admin_blocked", "password": "testpass123"},
        )

        self.assertEqual(login_response.status_code, 200)
        self.assertContains(login_response, "Client users are not allowed to access the admin site.")

        self.client.force_login(User.objects.get(username="client_admin_blocked"))
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_admin_user_can_access_admin(self):
        admin_user = User.objects.create_user(
            username="real_admin",
            password="testpass123",
            email="real-admin@example.com",
            role=RoleChoices.ADMIN,
            is_staff=True,
            is_superuser=True,
        )

        logged_in = self.client.login(username="real_admin", password="testpass123")
        response = self.client.get("/admin/")

        self.assertTrue(logged_in)
        self.assertEqual(response.status_code, 200)

# Create your tests here.
