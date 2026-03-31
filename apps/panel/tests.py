from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse

from apps.access_control.models import OMClientAccess, UserClientAccess
from apps.accounts.models import RoleChoices, User
from apps.audit_logs.models import AuditAction, AuditLog
from apps.clients.models import Client, ClientType
from apps.dashboards.models import Dashboard, DashboardScope
from apps.devices.models import Device, DeviceType, Topic, TopicData
from apps.thresholds.models import DeviceThreshold


class PanelAccessTests(TestCase):
    def setUp(self):
        self.grid_type, _ = ClientType.objects.get_or_create(code="GRID_TIED", defaults={"name": "Grid-Tied"})
        self.scope, _ = DashboardScope.objects.get_or_create(code="MAIN", defaults={"name": "Main Dashboard"})
        Dashboard.objects.get_or_create(
            code="GRID_TIED_MAIN",
            defaults={"name": "Grid-Tied Main", "client_type": self.grid_type, "scope": self.scope},
        )

        self.client_obj = Client.objects.create(
            site_name="Panel Site",
            code="PANEL_SITE",
            client_type=self.grid_type,
            dashboard_scope=self.scope,
            address="Dhaka",
        )
        self.device = Device.objects.create(
            client=self.client_obj,
            name="Panel Device",
            serial_number="PANEL-DEVICE-001",
            device_type=DeviceType.SOLAR,
        )
        self.topic = Topic.objects.create(
            device=self.device,
            name="Panel State",
            code="panel.device.state",
        )
        TopicData.objects.create(
            topic=self.topic,
            payload={"value": 52.1, "unit": "kW"},
            recorded_at="2026-03-31T10:00:00Z",
        )
        DeviceThreshold.objects.create(device=self.device, key="voltage_max", value="230.50", unit="V")

        self.admin_user = User.objects.create_user(
            username="panel_admin",
            password="testpass123",
            email="panel-admin@example.com",
            role=RoleChoices.ADMIN,
        )
        self.om_user = User.objects.create_user(
            username="panel_om",
            password="testpass123",
            email="panel-om@example.com",
            role=RoleChoices.OM,
        )
        OMClientAccess.objects.create(om_user=self.om_user, client=self.client_obj)

    def test_login_page_is_available(self):
        response = self.client.get(reverse("panel:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Green Power EMS Panel")

    def test_panel_login_writes_audit_log(self):
        response = self.client.post(
            reverse("panel:login"),
            {"username": "panel_admin", "password": "testpass123"},
        )

        self.assertEqual(response.status_code, 302)
        audit_log = AuditLog.objects.get(action=AuditAction.LOGIN)
        self.assertEqual(audit_log.actor.username, "panel_admin")
        self.assertEqual(audit_log.metadata["source"], "panel")

    def test_om_user_can_access_thresholds_page(self):
        self.client.login(username="panel_om", password="testpass123")
        response = self.client.get(reverse("panel:thresholds"), {"client_id": str(self.client_obj.id)})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "voltage_max")

    def test_om_dashboard_hides_client_warning_and_clients_card(self):
        self.client.login(username="panel_om", password="testpass123")
        response = self.client.get(reverse("panel:home"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Select a client from the top bar to load your dashboard data.")
        self.assertNotContains(response, '<span class="panel-card-label">Clients</span>', html=True)

    def test_admin_user_can_access_user_list(self):
        self.client.login(username="panel_admin", password="testpass123")
        response = self.client.get(reverse("panel:users"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "panel_admin")

    def test_admin_sidebar_shows_grouped_navigation_and_client_types(self):
        self.client.login(username="panel_admin", password="testpass123")
        response = self.client.get(reverse("panel:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="panel-nav-link is-active"', html=False)
        self.assertContains(response, "Dashboard")
        self.assertContains(response, "Client")
        self.assertContains(response, "Device")
        self.assertContains(response, "Access Control")
        self.assertContains(response, "Thresholds")
        self.assertContains(response, "Audit Logs")
        self.assertContains(response, reverse("panel:client-types"))

    def test_admin_can_open_client_types_page(self):
        self.client.login(username="panel_admin", password="testpass123")
        response = self.client.get(reverse("panel:client-types"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Client Types")
        self.assertContains(response, "Grid-Tied")

    def test_admin_can_filter_users_by_role_status_and_username(self):
        User.objects.create_user(
            username="client_lookup",
            password="testpass123",
            email="inactive-client@example.com",
            first_name="Inactive",
            last_name="Client",
            role=RoleChoices.CLIENT,
            is_active=True,
        )
        User.objects.create_user(
            username="inactive_admin_user",
            password="testpass123",
            email="other-admin@example.com",
            first_name="Inactive",
            last_name="Admin",
            role=RoleChoices.ADMIN,
            is_active=False,
        )

        self.client.login(username="panel_admin", password="testpass123")
        response = self.client.get(
            reverse("panel:users"),
            {"role": RoleChoices.CLIENT, "status": "active", "q": "inactive"},
        )

        self.assertEqual(response.status_code, 200)
        usernames = list(response.context["users"].values_list("username", flat=True))
        self.assertEqual(usernames, ["client_lookup"])

        response = self.client.get(
            reverse("panel:users"),
            {"status": "inactive", "q": "inactive"},
        )

        self.assertEqual(response.status_code, 200)
        usernames = list(response.context["users"].values_list("username", flat=True))
        self.assertEqual(usernames, ["inactive_admin_user"])

    def test_admin_dashboard_shows_management_shortcuts(self):
        self.client.login(username="panel_admin", password="testpass123")
        response = self.client.get(reverse("panel:home"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Management Shortcuts")
        self.assertNotContains(response, '<span class="panel-card-label">Thresholds</span>', html=True)

    def test_admin_can_create_user_from_panel(self):
        self.client.login(username="panel_admin", password="testpass123")
        group = Group.objects.create(name="Panel Managers")
        permission = Permission.objects.get(codename="view_client")
        response = self.client.post(
            reverse("panel:user-add"),
            {
                "username": "created_admin",
                "email": "created-admin@example.com",
                "first_name": "Created",
                "last_name": "Admin",
                "phone": "01700000000",
                "role": RoleChoices.ADMIN,
                "groups": [str(group.id)],
                "user_permissions": [str(permission.id)],
                "is_active": "on",
                "is_staff": "on",
                "password": "StrongPass123!",
            },
        )

        self.assertRedirects(response, reverse("panel:users"))
        created_user = User.objects.get(username="created_admin", role=RoleChoices.ADMIN)
        self.assertEqual(created_user.groups.count(), 1)
        self.assertEqual(created_user.user_permissions.count(), 1)
        audit_log = AuditLog.objects.filter(action=AuditAction.CREATE, target_type="User").latest("created_at")
        self.assertEqual(audit_log.actor.username, "panel_admin")
        self.assertEqual(audit_log.metadata["source"], "panel")

    def test_admin_can_create_client_from_panel(self):
        self.client.login(username="panel_admin", password="testpass123")
        response = self.client.post(
            reverse("panel:client-add"),
            {
                "site_name": "New Panel Site",
                "code": "",
                "client_type": str(self.grid_type.id),
                "dashboard_scope": str(self.scope.id),
                "address": "Chattogram",
                "is_active": "on",
            },
        )

        self.assertRedirects(response, reverse("panel:clients"))
        self.assertTrue(Client.objects.filter(site_name="New Panel Site", code="NEW_PANEL_SITE").exists())

    def test_admin_can_filter_clients_by_type_code_and_site_name(self):
        industry_type, _ = ClientType.objects.get_or_create(code="INDUSTRY", defaults={"name": "Industry"})
        board_scope, _ = DashboardScope.objects.get_or_create(code="BOARD", defaults={"name": "Board Dashboard"})
        Client.objects.create(
            site_name="Industry Test Site",
            code="INDUSTRY_TEST_SITE",
            client_type=industry_type,
            dashboard_scope=board_scope,
            address="Khulna",
        )
        Client.objects.create(
            site_name="Grid Searchable Site",
            code="GRID_SEARCHABLE_SITE",
            client_type=self.grid_type,
            dashboard_scope=self.scope,
            address="Rajshahi",
        )

        self.client.login(username="panel_admin", password="testpass123")
        response = self.client.get(
            reverse("panel:clients"),
            {
                "client_type": str(self.grid_type.id),
                "scope": str(self.scope.id),
                "q": "Grid Search",
            },
        )

        self.assertEqual(response.status_code, 200)
        client_codes = list(response.context["clients"].values_list("code", flat=True))
        self.assertEqual(client_codes, ["GRID_SEARCHABLE_SITE"])

    def test_admin_can_open_client_create_form(self):
        self.client.login(username="panel_admin", password="testpass123")
        response = self.client.get(reverse("panel:client-add"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Client")
        self.assertContains(response, "Company / Site Name")

    def test_admin_can_update_client_from_panel(self):
        self.client.login(username="panel_admin", password="testpass123")
        response = self.client.post(
            reverse("panel:client-edit", args=[self.client_obj.id]),
            {
                "site_name": "Updated Panel Site",
                "code": self.client_obj.code,
                "client_type": str(self.grid_type.id),
                "dashboard_scope": str(self.scope.id),
                "address": "Updated Address",
                "is_active": "on",
            },
        )

        self.assertRedirects(response, reverse("panel:clients"))
        self.client_obj.refresh_from_db()
        self.assertEqual(self.client_obj.site_name, "Updated Panel Site")
        self.assertEqual(self.client_obj.address, "Updated Address")

    def test_admin_can_delete_client_from_panel(self):
        self.client.login(username="panel_admin", password="testpass123")
        delete_client = Client.objects.create(
            site_name="Delete Panel Site",
            code="DELETE_PANEL_SITE",
            client_type=self.grid_type,
            dashboard_scope=self.scope,
            address="Khulna",
        )

        response = self.client.post(reverse("panel:client-delete", args=[delete_client.id]))

        self.assertRedirects(response, reverse("panel:clients"))
        self.assertFalse(Client.objects.filter(id=delete_client.id).exists())

    def test_admin_can_update_device_from_panel(self):
        self.client.login(username="panel_admin", password="testpass123")
        response = self.client.post(
            reverse("panel:device-edit", args=[self.device.id]),
            {
                "client": str(self.client_obj.id),
                "name": "Updated Device",
                "serial_number": self.device.serial_number,
                "device_type": DeviceType.BESS,
                "installed_at": "",
                "is_active": "on",
            },
        )

        self.assertRedirects(response, reverse("panel:devices"))
        self.device.refresh_from_db()
        self.assertEqual(self.device.name, "Updated Device")
        self.assertEqual(self.device.device_type, DeviceType.BESS)

    def test_admin_can_delete_device_state_from_panel(self):
        self.client.login(username="panel_admin", password="testpass123")
        delete_topic = Topic.objects.create(
            device=self.device,
            name="Delete State",
            code="delete.panel.state",
        )

        response = self.client.post(reverse("panel:device-state-delete", args=[delete_topic.id]))

        self.assertRedirects(response, reverse("panel:device-states"))
        self.assertFalse(Topic.objects.filter(id=delete_topic.id).exists())

    def test_om_user_cannot_access_admin_create_pages(self):
        self.client.login(username="panel_om", password="testpass123")
        response = self.client.get(reverse("panel:user-add"))

        self.assertEqual(response.status_code, 403)

    def test_client_user_cannot_log_into_panel(self):
        client_user = User.objects.create_user(
            username="panel_client",
            password="testpass123",
            email="panel-client@example.com",
            role=RoleChoices.CLIENT,
        )
        UserClientAccess.objects.create(user=client_user, client=self.client_obj)
        response = self.client.post(
            reverse("panel:login"),
            {"username": "panel_client", "password": "testpass123"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Client users must use the React client portal")

    def test_panel_logout_writes_audit_log(self):
        self.client.login(username="panel_admin", password="testpass123")

        response = self.client.post(reverse("panel:logout"))

        self.assertEqual(response.status_code, 302)
        audit_log = AuditLog.objects.get(action=AuditAction.LOGOUT)
        self.assertEqual(audit_log.actor.username, "panel_admin")
        self.assertEqual(audit_log.metadata["source"], "panel")
