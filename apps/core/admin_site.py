from django.contrib import admin
from django.contrib.admin.forms import AdminAuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import RoleChoices


class HardenedAdminAuthenticationForm(AdminAuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if getattr(user, "role", None) == RoleChoices.CLIENT:
            raise ValidationError(
                _("Client users are not allowed to access the admin site."),
                code="invalid_login",
            )


class HardenedAdminSite(admin.AdminSite):
    site_header = "Green Power EMS Administration"
    site_title = "Green Power EMS Admin"
    index_title = "Administration"
    login_form = HardenedAdminAuthenticationForm

    def has_permission(self, request):
        user = request.user
        return (
            user.is_active
            and user.is_staff
            and getattr(user, "role", None) in {RoleChoices.ADMIN, RoleChoices.OM}
        )


admin.autodiscover()
hardened_admin_site = HardenedAdminSite(name="hardened_admin")

for model, model_admin in admin.site._registry.items():
    hardened_admin_site.register(model, model_admin.__class__)
