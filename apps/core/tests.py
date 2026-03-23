from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.access_control.models import OMClientAccess, UserClientAccess
from apps.accounts.models import User
from apps.clients.models import Client
from apps.dashboards.models import ClientType, DashboardScope
from apps.devices.models import Device, Topic, TopicData


class IntegrationSeedCommandTests(TestCase):
    def test_seed_integration_data_creates_frontend_ready_records(self):
        stdout = StringIO()

        call_command("seed_integration_data", password="SeedPass123!", stdout=stdout)

        self.assertTrue(User.objects.filter(username="admin_demo").exists())
        self.assertTrue(User.objects.filter(username="om_demo").exists())
        self.assertTrue(User.objects.filter(username="client_grid_management").exists())
        self.assertTrue(ClientType.objects.filter(code="GRID_TIED").exists())
        self.assertTrue(DashboardScope.objects.filter(code="MANAGEMENT").exists())
        self.assertTrue(Client.objects.filter(code="GRID_SITE_ALPHA").exists())
        self.assertTrue(Client.objects.filter(code="GRID_SITE_ALPHA", dashboard_scope__code="MANAGEMENT").exists())
        self.assertTrue(UserClientAccess.objects.filter(user__username="client_grid_management").exists())
        self.assertTrue(OMClientAccess.objects.filter(om_user__username="om_demo").count() >= 2)
        self.assertTrue(Device.objects.filter(serial_number="GRID-INV-001").exists())
        self.assertTrue(Topic.objects.filter(code="grid.alpha.inverter.status").exists())
        self.assertTrue(Topic.objects.filter(code="mqtt_rt_data").exists())
        self.assertTrue(Topic.objects.filter(code="mqtt_eny_now").exists())
        self.assertTrue(Topic.objects.filter(code="mqtt_day_data").exists())
        self.assertTrue(Topic.objects.filter(code="mqtt_frz_data").exists())
        self.assertTrue(TopicData.objects.filter(topic__code="mqtt_rt_data").exists())

# Create your tests here.
