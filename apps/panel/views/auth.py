from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

from apps.accounts.models import RoleChoices
from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import write_audit_log


class PanelLoginView(LoginView):
    template_name = "panel/auth/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.user.role == RoleChoices.CLIENT:
            logout(self.request)
            form.add_error(None, "Client users must use the React client portal, not the internal panel.")
            return self.form_invalid(form)
        write_audit_log(
            actor=self.request.user,
            action=AuditAction.LOGIN,
            target_type="User",
            target_id=self.request.user.pk,
            description=f"User {self.request.user.username} logged in via panel",
            metadata={"source": "panel", "path": self.request.path, "method": self.request.method},
        )
        return response

    def get_success_url(self):
        return reverse_lazy("panel:home")


class PanelLogoutView(LogoutView):
    next_page = reverse_lazy("panel:login")

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            write_audit_log(
                actor=request.user,
                action=AuditAction.LOGOUT,
                target_type="User",
                target_id=request.user.pk,
                description=f"User {request.user.username} logged out from panel",
                metadata={"source": "panel", "path": request.path, "method": request.method},
            )
        return super().post(request, *args, **kwargs)
