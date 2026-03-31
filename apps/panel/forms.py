from django import forms
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy

from apps.access_control.models import OMClientAccess, UserClientAccess
from apps.accounts.models import RoleChoices, User
from apps.clients.forms import ClientAdminForm
from apps.clients.models import Client, ClientType
from apps.devices.models import Device, Topic, TopicData
from apps.thresholds.models import DeviceThreshold


class LabeledModelChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, label_getter=None, **kwargs):
        self.label_getter = label_getter
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        if self.label_getter:
            return self.label_getter(obj)
        return super().label_from_instance(obj)


class LabeledModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, *args, label_getter=None, **kwargs):
        self.label_getter = label_getter
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        if self.label_getter:
            return self.label_getter(obj)
        return super().label_from_instance(obj)


class UserPanelForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="Set a password on create. Leave blank on edit to keep the current password.",
    )
    groups = LabeledModelMultipleChoiceField(
        queryset=Group.objects.order_by("name"),
        required=False,
        widget=forms.SelectMultiple(attrs={"size": 8}),
        help_text="Groups define reusable permission bundles.",
    )
    user_permissions = LabeledModelMultipleChoiceField(
        queryset=Permission.objects.select_related("content_type").order_by(
            "content_type__app_label",
            "content_type__model",
            "name",
        ),
        required=False,
        widget=forms.SelectMultiple(attrs={"size": 12}),
        label="User permissions",
        label_getter=lambda permission: (
            f"{permission.content_type.app_label} | {permission.content_type.model} | {permission.name}"
        ),
        help_text="Direct permissions should be used sparingly. Prefer groups when possible.",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "role",
            "groups",
            "user_permissions",
            "is_active",
            "is_staff",
            "is_superuser",
            "password",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["password"].required = True
        self.fields["groups"].queryset = Group.objects.order_by("name")
        self.fields["user_permissions"].queryset = Permission.objects.select_related("content_type").order_by(
            "content_type__app_label",
            "content_type__model",
            "name",
        )

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")

        if role == RoleChoices.CLIENT and cleaned_data.get("is_staff"):
            raise ValidationError({"is_staff": "Client users should not be granted internal panel or admin access."})

        if role in {RoleChoices.ADMIN, RoleChoices.OM} and not cleaned_data.get("is_staff"):
            raise ValidationError({"is_staff": "Admin and O&M users need staff access for internal operations."})

        return cleaned_data

    def save(self, commit=True):
        password = self.cleaned_data.get("password")
        user = super().save(commit=False)
        if password:
            user.set_password(password)
        if commit:
            user.save()
            self.save_m2m()
        return user


class ClientPanelForm(ClientAdminForm):
    class Meta(ClientAdminForm.Meta):
        model = Client
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["dashboard_scope"].widget.attrs["data-scope-options-url"] = reverse_lazy("panel:client-scope-options")
        self.fields["code"].widget.attrs["data-code-suggestion-url"] = reverse_lazy("panel:client-code-suggestion")
        self.fields["code"].widget.attrs["data-code-validation-url"] = reverse_lazy("panel:client-code-validation")
        self.fields["code"].widget.attrs["data-client-id"] = str(self.instance.pk) if self.instance.pk else ""


class ClientTypePanelForm(forms.ModelForm):
    class Meta:
        model = ClientType
        fields = ["name", "code", "is_active"]


class UserClientAccessPanelForm(forms.ModelForm):
    user = LabeledModelChoiceField(
        queryset=User.objects.none(),
        label="Client user",
        label_getter=lambda user: f"{user.username} ({user.get_full_name() or user.email})",
    )
    client = LabeledModelChoiceField(
        queryset=Client.objects.none(),
        label_getter=lambda client: f"{client.site_name} ({client.code})",
    )

    class Meta:
        model = UserClientAccess
        fields = ["user", "client", "is_default", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        available_users = User.objects.filter(role=RoleChoices.CLIENT).order_by("username")
        available_clients = Client.objects.order_by("site_name")

        if self.instance.pk:
            available_clients = available_clients.exclude(client_users__isnull=False) | Client.objects.filter(
                pk=self.instance.client_id
            )
        else:
            available_clients = available_clients.exclude(client_users__isnull=False)

        self.fields["user"].queryset = available_users.distinct()
        self.fields["client"].queryset = available_clients.distinct().order_by("site_name")

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get("user")
        client = cleaned_data.get("client")

        if user and user.role != RoleChoices.CLIENT:
            raise ValidationError({"user": "Only users with role Client can be assigned here."})

        if client:
            duplicate_qs = UserClientAccess.objects.filter(client=client)
            if self.instance.pk:
                duplicate_qs = duplicate_qs.exclude(pk=self.instance.pk)
            if duplicate_qs.exists():
                raise ValidationError({"client": "This client is already linked to another user."})

        return cleaned_data

    def save(self, commit=True):
        assignment = super().save(commit=commit)
        if commit and assignment.is_default:
            UserClientAccess.objects.filter(user=assignment.user).exclude(pk=assignment.pk).update(is_default=False)
        return assignment


class OMClientAccessPanelForm(forms.ModelForm):
    om_user = LabeledModelChoiceField(
        queryset=User.objects.none(),
        label="O&M user",
        label_getter=lambda user: f"{user.username} ({user.get_full_name() or user.email})",
    )
    client = LabeledModelChoiceField(
        queryset=Client.objects.none(),
        label_getter=lambda client: f"{client.site_name} ({client.code})",
    )

    class Meta:
        model = OMClientAccess
        fields = ["om_user", "client"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["om_user"].queryset = User.objects.filter(role=RoleChoices.OM).order_by("username")
        self.fields["client"].queryset = Client.objects.order_by("site_name")

    def clean(self):
        cleaned_data = super().clean()
        om_user = cleaned_data.get("om_user")
        if om_user and om_user.role != RoleChoices.OM:
            raise ValidationError({"om_user": "Only users with role O&M can be assigned here."})
        return cleaned_data


class DevicePanelForm(forms.ModelForm):
    client = LabeledModelChoiceField(
        queryset=Client.objects.order_by("site_name"),
        label_getter=lambda client: f"{client.site_name} ({client.code})",
    )

    class Meta:
        model = Device
        fields = ["client", "name", "serial_number", "device_type", "installed_at", "is_active"]
        widgets = {
            "installed_at": forms.DateInput(attrs={"type": "date"}),
        }


class TopicPanelForm(forms.ModelForm):
    device = LabeledModelChoiceField(
        queryset=Device.objects.select_related("client").order_by("name"),
        label_getter=lambda device: f"{device.name} ({device.serial_number}) - {device.client.site_name}",
    )

    class Meta:
        model = Topic
        fields = ["device", "name", "code", "description", "is_active"]


class TopicDataPanelForm(forms.ModelForm):
    topic = LabeledModelChoiceField(
        queryset=Topic.objects.select_related("device", "device__client").order_by("code"),
        label_getter=lambda topic: f"{topic.code} - {topic.device.client.site_name}",
    )
    payload = forms.JSONField(widget=forms.Textarea(attrs={"rows": 6}))

    class Meta:
        model = TopicData
        fields = ["topic", "payload", "recorded_at"]
        widgets = {
            "recorded_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["recorded_at"].input_formats = ["%Y-%m-%dT%H:%M"]


class DeviceThresholdPanelForm(forms.ModelForm):
    device = LabeledModelChoiceField(
        queryset=Device.objects.select_related("client").order_by("name"),
        label_getter=lambda device: f"{device.name} ({device.serial_number}) - {device.client.site_name}",
    )

    class Meta:
        model = DeviceThreshold
        fields = ["device", "key", "value", "unit"]
