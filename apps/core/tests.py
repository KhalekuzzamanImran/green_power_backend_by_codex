from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.access_control.models import ClientDashboardAccess, ClientProfile, OMClientAccess
from apps.accounts.models import User
from apps.clients.models import Client
from apps.devices.models import Device


class IntegrationSeedCommandTests(TestCase):
    def test_seed_integration_data_creates_frontend_ready_records(self):
        stdout = StringIO()

        call_command("seed_integration_data", password="SeedPass123!", stdout=stdout)

        self.assertTrue(User.objects.filter(username="admin_demo").exists())
        self.assertTrue(User.objects.filter(username="om_demo").exists())
        self.assertTrue(User.objects.filter(username="client_grid_management").exists())
        self.assertTrue(Client.objects.filter(code="GRID_SITE_ALPHA").exists())
        self.assertTrue(ClientProfile.objects.filter(user__username="client_grid_management").exists())
        self.assertTrue(OMClientAccess.objects.filter(om_user__username="om_demo").count() >= 2)
        self.assertTrue(ClientDashboardAccess.objects.filter(client_user__username="client_grid_management").exists())
        self.assertTrue(Device.objects.filter(serial_number="GRID-INV-001").exists())

# Create your tests here.
