from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.access_control.models import OMClientAccess
from apps.accounts.models import RoleChoices, User
from apps.clients.models import Client


class ClientAccessTests(APITestCase):
    def setUp(self):
        self.om_user = User.objects.create_user(
            username="om_user",
            password="testpass123",
            email="om@example.com",
            role=RoleChoices.OM,
        )
        self.client_allowed = Client.objects.create(name="Allowed Client", code="ALLOWED")
        self.client_blocked = Client.objects.create(name="Blocked Client", code="BLOCKED")
        OMClientAccess.objects.create(om_user=self.om_user, client=self.client_allowed)
        refresh = RefreshToken.for_user(self.om_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_om_only_sees_assigned_clients(self):
        response = self.client.get("/api/v1/clients/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_codes = {row["code"] for row in response.data}
        self.assertEqual(returned_codes, {"ALLOWED"})

# Create your tests here.
