from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.access_control.models import OMClientAccess, UserClientAccess
from apps.accounts.models import RoleChoices, User
from apps.clients.models import Client
from apps.dashboards.models import ClientType, DashboardScope
from apps.devices.models import Device, DeviceType, Topic, TopicData


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
        self.grid_type, _ = ClientType.objects.get_or_create(code="GRID_TIED", defaults={"name": "Grid-Tied"})
        self.industry_type, _ = ClientType.objects.get_or_create(code="INDUSTRY", defaults={"name": "Industry"})
        self.scope, _ = DashboardScope.objects.get_or_create(code="MAIN", defaults={"name": "Main Dashboard"})
        self.client_allowed = Client.objects.create(
            name="Client Allowed",
            code="CLIENT_ALLOWED",
            client_type=self.grid_type,
            dashboard_scope=self.scope,
        )
        self.client_other = Client.objects.create(
            name="Client Other",
            code="CLIENT_OTHER",
            client_type=self.industry_type,
            dashboard_scope=self.scope,
        )
        UserClientAccess.objects.create(user=self.client_user, client=self.client_allowed)
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
        self.topic_allowed = Topic.objects.create(
            device=self.device_allowed,
            name="Allowed Topic",
            code="allowed.topic",
        )
        self.topic_other = Topic.objects.create(
            device=self.device_other,
            name="Other Topic",
            code="other.topic",
        )
        self.topic_allowed_data = TopicData.objects.create(
            topic=self.topic_allowed,
            payload={"value": 52.3, "unit": "kW"},
            recorded_at="2026-03-23T10:00:00Z",
        )
        self.topic_other_data = TopicData.objects.create(
            topic=self.topic_other,
            payload={"value": 12.1, "unit": "kW"},
            recorded_at="2026-03-23T10:05:00Z",
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

    def test_client_only_sees_topics_for_own_devices(self):
        refresh = RefreshToken.for_user(self.client_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.get("/api/v1/topics/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        codes = {row["code"] for row in response.data}
        self.assertEqual(codes, {"allowed.topic"})

    def test_client_can_fetch_device_topics_for_owned_device(self):
        refresh = RefreshToken.for_user(self.client_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.get(f"/api/v1/devices/{self.device_allowed.id}/topics/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        codes = {row["code"] for row in response.data}
        self.assertEqual(codes, {"allowed.topic"})

    def test_client_only_sees_topic_data_for_own_topics(self):
        refresh = RefreshToken.for_user(self.client_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.get("/api/v1/topic-data/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        topic_codes = {row["topic_code"] for row in response.data}
        self.assertEqual(topic_codes, {"allowed.topic"})

    def test_client_can_fetch_topic_wise_data_for_owned_topic(self):
        refresh = RefreshToken.for_user(self.client_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.get(f"/api/v1/topics/{self.topic_allowed.id}/data/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["topic_code"], "allowed.topic")

    def test_topic_data_supports_topic_code_filter(self):
        refresh = RefreshToken.for_user(self.client_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.get("/api/v1/topic-data/?topic_code=allowed.topic")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["topic_code"], "allowed.topic")

    def test_multi_client_user_must_pass_client_id_for_devices(self):
        second_client = Client.objects.create(
            name="Second Allowed Client",
            code="SECOND_ALLOWED",
            client_type=self.grid_type,
            dashboard_scope=self.scope,
        )
        UserClientAccess.objects.create(user=self.client_user, client=second_client)

        refresh = RefreshToken.for_user(self.client_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.get("/api/v1/devices/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("client_id", response.data)

    def test_multi_client_user_can_filter_devices_by_selected_client(self):
        second_client = Client.objects.create(
            name="Second Allowed Client",
            code="SECOND_ALLOWED_2",
            client_type=self.grid_type,
            dashboard_scope=self.scope,
        )
        second_device = Device.objects.create(
            client=second_client,
            name="Second Device",
            serial_number="SN-SECOND",
            device_type=DeviceType.SOLAR,
        )
        UserClientAccess.objects.create(user=self.client_user, client=second_client)

        refresh = RefreshToken.for_user(self.client_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.get(f"/api/v1/devices/?client_id={second_client.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serials = {row["serial_number"] for row in response.data}
        self.assertEqual(serials, {second_device.serial_number})
