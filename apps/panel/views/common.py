from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView

from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import audit_model_event, get_action_label
from apps.panel.navigation import build_panel_navigation
from apps.panel.permissions import AdminOnlyMixin


class PanelAdminContextMixin(AdminOnlyMixin):
    form_template_name = "panel/form.html"
    delete_template_name = "panel/confirm_delete.html"
    success_message = ""
    page_heading = ""
    active_nav_key = ""
    success_url_name = "panel:home"
    audit_source = "panel"
    audit_action_create = AuditAction.CREATE
    audit_action_update = AuditAction.UPDATE
    audit_action_delete = AuditAction.DELETE

    def get_success_url(self):
        return reverse_lazy(self.success_url_name)

    def get_cancel_url(self):
        return self.get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav_items"] = build_panel_navigation(self.request.user)
        context["page_heading"] = self.page_heading or self.page_title
        context["page_title"] = self.page_title
        context["cancel_url"] = self.get_cancel_url()
        context["submit_label"] = "Save"
        return context

    def _notify_success(self):
        if self.success_message:
            messages.success(self.request, self.success_message)

    def get_audit_description(self, action, instance):
        return f"{get_action_label(action)} {instance.__class__.__name__} {instance}"

    def write_audit(self, *, action, instance, changed_fields=None):
        return audit_model_event(
            actor=self.request.user,
            action=action,
            instance=instance,
            description=self.get_audit_description(action, instance),
            request=self.request,
            source=self.audit_source,
            changed_fields=changed_fields,
        )


class PanelCreateView(PanelAdminContextMixin, CreateView):
    template_name = PanelAdminContextMixin.form_template_name

    def form_valid(self, form):
        response = super().form_valid(form)
        self.write_audit(action=self.audit_action_create, instance=self.object)
        self._notify_success()
        return response


class PanelUpdateView(PanelAdminContextMixin, UpdateView):
    template_name = PanelAdminContextMixin.form_template_name

    def form_valid(self, form):
        changed_fields = list(form.changed_data)
        response = super().form_valid(form)
        self.write_audit(action=self.audit_action_update, instance=self.object, changed_fields=changed_fields)
        self._notify_success()
        return response


class PanelDeleteView(PanelAdminContextMixin, DeleteView):
    template_name = PanelAdminContextMixin.delete_template_name

    def form_valid(self, form):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.write_audit(action=self.audit_action_delete, instance=self.object)
        self.object.delete()
        self._notify_success()
        return HttpResponseRedirect(success_url)
