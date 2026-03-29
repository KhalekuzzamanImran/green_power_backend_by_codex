from django import forms
from django.core.exceptions import ValidationError

from apps.clients.models import Client
from apps.dashboards.models import Dashboard, DashboardScope


def get_dashboard_scope_queryset(client_type_id):
    if not client_type_id:
        return DashboardScope.objects.none()

    return DashboardScope.objects.filter(
        dashboards__client_type_id=client_type_id,
        dashboards__is_active=True,
        is_active=True,
    ).distinct().order_by("name")


class ClientAdminForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        client_type_id = self.data.get("client_type")
        if not client_type_id and self.instance.pk:
            client_type_id = self.instance.client_type_id

        self.fields["dashboard_scope"].queryset = get_dashboard_scope_queryset(client_type_id)

        if not client_type_id:
            self.fields["dashboard_scope"].help_text = "Select client type first."

    def clean(self):
        cleaned_data = super().clean()
        client_type = cleaned_data.get("client_type")
        dashboard_scope = cleaned_data.get("dashboard_scope")

        if client_type and dashboard_scope and not Dashboard.objects.filter(
            client_type=client_type,
            scope=dashboard_scope,
            is_active=True,
        ).exists():
            raise ValidationError(
                {"dashboard_scope": "Selected dashboard scope is not available for this client type."}
            )

        return cleaned_data
