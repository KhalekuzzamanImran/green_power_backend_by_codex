from django.urls import reverse

from apps.accounts.models import RoleChoices


def build_panel_navigation(user):
    sections = [
        {
            "label": "Dashboard",
            "icon": "dashboard",
            "key": "dashboard",
            "url": reverse("panel:home"),
            "items": [],
        },
        {
            "label": "Client",
            "icon": "client",
            "key": "client_group",
            "items": [
                {"label": "Clients", "url": reverse("panel:clients"), "key": "clients"},
                {"label": "Client Types", "url": reverse("panel:client-types"), "key": "client_types"},
            ],
        },
        {
            "label": "Device",
            "icon": "device",
            "key": "device_group",
            "items": [
                {"label": "Devices", "url": reverse("panel:devices"), "key": "devices"},
                {"label": "Device States", "url": reverse("panel:device-states"), "key": "device_states"},
                {"label": "Device Data", "url": reverse("panel:device-data"), "key": "device_data"},
            ],
        },
    ]

    if user.role in {RoleChoices.ADMIN, RoleChoices.OM}:
        sections.append(
            {
                "label": "Thresholds",
                "icon": "thresholds",
                "key": "thresholds",
                "url": reverse("panel:thresholds"),
                "items": [],
            }
        )

    if user.role == RoleChoices.ADMIN:
        sections.extend(
            [
                {
                    "label": "Access Control",
                    "icon": "access-control",
                    "key": "access_control_group",
                    "items": [
                        {"label": "Users", "url": reverse("panel:users"), "key": "users"},
                        {"label": "Client Access", "url": reverse("panel:user-client-access"), "key": "user_client_access"},
                        {"label": "O&M Access", "url": reverse("panel:om-client-access"), "key": "om_client_access"},
                    ],
                },
                {
                    "label": "Audit Logs",
                    "icon": "audit-logs",
                    "key": "audit_logs",
                    "url": reverse("panel:audit-logs"),
                    "items": [],
                },
            ]
        )

    return sections
