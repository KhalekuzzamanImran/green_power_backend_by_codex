from django.core.exceptions import PermissionDenied
from django.db.models import Case, IntegerField, Q, Value, When
from django.views.generic import TemplateView

from apps.accounts.models import RoleChoices, User
from apps.panel.forms import UserPanelForm
from apps.panel.navigation import build_panel_navigation
from apps.panel.permissions import AdminOnlyMixin
from apps.panel.views.common import PanelCreateView, PanelDeleteView, PanelUpdateView


class UserListView(AdminOnlyMixin, TemplateView):
    template_name = "panel/users/list.html"
    page_title = "Users"
    active_nav_key = "users"

    def get_template_names(self):
        if self.request.headers.get("X-Panel-Partial") == "users-results":
            return ["panel/users/partials/results.html"]
        return [self.template_name]

    def get_filtered_users(self):
        role = self.request.GET.get("role")
        status = (self.request.GET.get("status") or "").strip().lower()
        if not status and self.request.GET.get("active") == "1":
            status = "active"
        search_query = self.request.GET.get("q", "").strip()

        users = User.objects.only(
            "id",
            "username",
            "first_name",
            "last_name",
            "role",
            "is_active",
        )

        if role:
            users = users.filter(role=role)
        if status == "active":
            users = users.filter(is_active=True)
        elif status == "inactive":
            users = users.filter(is_active=False)

        search_terms = [term for term in search_query.split() if term][:3]
        if search_terms:
            for term in search_terms:
                users = users.filter(
                    Q(username__istartswith=term)
                    | Q(first_name__istartswith=term)
                    | Q(last_name__istartswith=term)
                )

            if len(search_terms) == 1:
                term = search_terms[0]
                users = users.annotate(
                    search_rank=Case(
                        When(username__istartswith=term, then=Value(0)),
                        When(first_name__istartswith=term, then=Value(1)),
                        When(last_name__istartswith=term, then=Value(2)),
                        default=Value(3),
                        output_field=IntegerField(),
                    )
                ).order_by("search_rank", "username")
            else:
                users = users.order_by("username")
        else:
            users = users.order_by("username")

        return users, role or "", status, search_query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users, selected_role, selected_status, search_query = self.get_filtered_users()
        context["nav_items"] = build_panel_navigation(self.request.user)
        context["users"] = users
        context["selected_role"] = selected_role
        context["selected_status"] = selected_status
        context["search_query"] = search_query
        context["role_choices"] = RoleChoices.choices
        return context


class UserCreateView(PanelCreateView):
    model = User
    form_class = UserPanelForm
    page_title = "Create User"
    active_nav_key = "users"
    success_url_name = "panel:users"
    success_message = "User created successfully."


class UserUpdateView(PanelUpdateView):
    model = User
    form_class = UserPanelForm
    page_title = "Edit User"
    active_nav_key = "users"
    success_url_name = "panel:users"
    success_message = "User updated successfully."


class UserDeleteView(PanelDeleteView):
    model = User
    page_title = "Delete User"
    active_nav_key = "users"
    success_url_name = "panel:users"
    success_message = "User deleted successfully."

    def dispatch(self, request, *args, **kwargs):
        if str(request.user.pk) == str(kwargs["pk"]):
            raise PermissionDenied("You cannot delete the currently signed-in user.")
        return super().dispatch(request, *args, **kwargs)
