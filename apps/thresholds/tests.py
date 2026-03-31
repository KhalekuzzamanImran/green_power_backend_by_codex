from decimal import Decimal

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.access_control.models import OMClientAccess, UserClientAccess
from apps.accounts.models import RoleChoices, User
from apps.clients.models import Client, ClientType
from apps.dashboards.models import DashboardScope
from apps.devices.models import Device, DeviceType
from apps.thresholds.models import DeviceThreshold


class ThresholdPermissionTests(APITestCase):
    def setUp(self):
        self.om_user = User.objects.create_user(
            username="threshold_om",
            password="testpass123",
            email="threshold-om@example.com",
            role=RoleChoices.OM,
        )
        self.client_user = User.objects.create_user(
            username="threshold_client",
            password="testpass123",
            email="threshold-client@example.com",
            role=RoleChoices.CLIENT,
        )
        self.other_om_user = User.objects.create_user(
            username="threshold_other_om",
            password="testpass123",
            email="threshold-other-om@example.com",
            role=RoleChoices.OM,
        )
        self.grid_type, _ = ClientType.objects.get_or_create(code="GRID_TIED", defaults={"name": "Grid-Tied"})
        self.industry_type, _ = ClientType.objects.get_or_create(code="INDUSTRY", defaults={"name": "Industry"})
        self.scope, _ = DashboardScope.objects.get_or_create(code="MAIN", defaults={"name": "Main Dashboard"})
        self.client_obj = Client.objects.create(
            site_name="Threshold Client",
            code="THRESHOLD_CLIENT",
            client_type=self.grid_type,
            dashboard_scope=self.scope,
        )
        self.other_client_obj = Client.objects.create(
            site_name="Other Client",
            code="OTHER_CLIENT",
            client_type=self.industry_type,
            dashboard_scope=self.scope,
        )
        UserClientAccess.objects.create(user=self.client_user, client=self.client_obj)
        OMClientAccess.objects.create(om_user=self.om_user, client=self.client_obj)
        self.device = Device.objects.create(
            client=self.client_obj,
            name="Threshold Device",
            serial_number="SN-THRESHOLD",
            device_type=DeviceType.BESS,
        )
        self.other_device = Device.objects.create(
            client=self.other_client_obj,
            name="Other Threshold Device",
            serial_number="SN-OTHER-THRESHOLD",
            device_type=DeviceType.GRID,
        )

    def test_om_can_create_threshold_for_accessible_device(self):
        refresh = RefreshToken.for_user(self.om_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.post(
            "/api/v1/thresholds/",
            {
                "device": str(self.device.id),
                "key": "voltage_max",
                "value": "230.50",
                "unit": "V",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        threshold = DeviceThreshold.objects.get(device=self.device, key="voltage_max")
        self.assertEqual(threshold.value, Decimal("230.50"))
        self.assertEqual(threshold.updated_by, self.om_user)

    def test_client_cannot_create_threshold(self):
        refresh = RefreshToken.for_user(self.client_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.post(
            "/api/v1/thresholds/",
            {
                "device": str(self.device.id),
                "key": "temperature_max",
                "value": "40.00",
                "unit": "C",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_om_cannot_create_threshold_for_unassigned_device(self):
        OMClientAccess.objects.create(om_user=self.other_om_user, client=self.other_client_obj)
        refresh = RefreshToken.for_user(self.other_om_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.post(
            "/api/v1/thresholds/",
            {
                "device": str(self.device.id),
                "key": "current_max",
                "value": "100.00",
                "unit": "A",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
