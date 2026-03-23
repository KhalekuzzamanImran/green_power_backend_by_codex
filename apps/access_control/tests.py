from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.access_control.models import UserClientAccess
from apps.accounts.models import RoleChoices, User
from apps.clients.models import Client
from apps.dashboards.models import ClientType, DashboardScope


class UserClientAccessValidationTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="uca_admin",
            password="testpass123",
            email="uca-admin@example.com",
            role=RoleChoices.ADMIN,
        )
        self.client_user_one = User.objects.create_user(
            username="client_user_one",
            password="testpass123",
            email="client-one@example.com",
            role=RoleChoices.CLIENT,
        )
        self.client_user_two = User.objects.create_user(
            username="client_user_two",
            password="testpass123",
            email="client-two@example.com",
            role=RoleChoices.CLIENT,
        )
        self.om_user = User.objects.create_user(
            username="om_user_forbidden",
            password="testpass123",
            email="om-forbidden@example.com",
            role=RoleChoices.OM,
        )
        self.client_type, _ = ClientType.objects.get_or_create(code="GRID_TIED", defaults={"name": "Grid-Tied"})
        self.scope, _ = DashboardScope.objects.get_or_create(code="MAIN", defaults={"name": "Main Dashboard"})
        self.client_obj = Client.objects.create(
            name="Linked Client",
            code="LINKED_CLIENT",
            client_type=self.client_type,
            dashboard_scope=self.scope,
        )
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_rejects_non_client_role_user_for_user_client_access(self):
        response = self.client.post(
            "/api/v1/user-client-accesses/",
            {
                "user": str(self.om_user.id),
                "client": str(self.client_obj.id),
                "is_default": True,
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("user", response.data)

    def test_rejects_client_when_already_linked_to_another_user(self):
        UserClientAccess.objects.create(user=self.client_user_one, client=self.client_obj)

        response = self.client.post(
            "/api/v1/user-client-accesses/",
            {
                "user": str(self.client_user_two.id),
                "client": str(self.client_obj.id),
                "is_default": False,
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("client", response.data)
