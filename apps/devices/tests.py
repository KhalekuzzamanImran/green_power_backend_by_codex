from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.access_control.models import ClientProfile, OMClientAccess
from apps.accounts.models import RoleChoices, User
from apps.clients.models import Client
from apps.devices.models import Device, DeviceType


class DeviceVisibilityTests(APITestCase):
    def setUp(self):
        self.om_user = User.objects.create_user(
            username="ops_user",
            password="testpass123",
            email="ops@example.com",
            role=RoleChoices.OM,
        )
        self.client_user = User.objects.create_user(
            username="client_scope",
            password="testpass123",
            email="clientscope@example.com",
            role=RoleChoices.CLIENT,
        )
        self.client_allowed = Client.objects.create(name="Client Allowed", code="CLIENT_ALLOWED")
        self.client_other = Client.objects.create(name="Client Other", code="CLIENT_OTHER")
        ClientProfile.objects.create(user=self.client_user, client=self.client_allowed)
        OMClientAccess.objects.create(om_user=self.om_user, client=self.client_allowed)
        self.device_allowed = Device.objects.create(
            client=self.client_allowed,
            name="Allowed Device",
            serial_number="SN-ALLOWED",
            device_type=DeviceType.SOLAR,
        )
        self.device_other = Device.objects.create(
            client=self.client_other,
            name="Other Device",
            serial_number="SN-OTHER",
            device_type=DeviceType.GRID,
        )

    def test_om_only_sees_assigned_client_devices(self):
        refresh = RefreshToken.for_user(self.om_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.get("/api/v1/devices/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serials = {row["serial_number"] for row in response.data}
        self.assertEqual(serials, {"SN-ALLOWED"})

    def test_client_only_sees_own_client_devices(self):
        refresh = RefreshToken.for_user(self.client_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.get("/api/v1/devices/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serials = {row["serial_number"] for row in response.data}
        self.assertEqual(serials, {"SN-ALLOWED"})

# Create your tests here.
