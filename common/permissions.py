from __future__ import annotations

from typing import Iterable

from rest_framework.permissions import BasePermission


def _roles_from_token(request) -> set[str]:
    token = getattr(request, "auth", None)
    if token and "roles" in token:
        roles = token.get("roles")
        if isinstance(roles, (list, tuple, set)):
            return set(str(role) for role in roles)
    return set()


def _roles_from_user(request) -> set[str]:
    user = getattr(request, "user", None)
    if not user or not getattr(user, "is_authenticated", False):
        return set()
    roles = {"user"}
    roles.update(user.groups.values_list("name", flat=True))
    if getattr(user, "role", None):
        roles.add(user.role.key)
    if user.is_staff:
        roles.add("staff")
    if user.is_superuser:
        roles.add("admin")
    if "Staff" in roles:
        roles.add("staff")
    if "Admin" in roles:
        roles.add("admin")
    return roles


class HasRole(BasePermission):
    required_roles: Iterable[str] | None = None

    def has_permission(self, request, view) -> bool:
        required = getattr(view, "required_roles", None) or self.required_roles
        if not required:
            return True
        required_set = {str(role) for role in required}
        roles = _roles_from_token(request) or _roles_from_user(request)
        return bool(roles.intersection(required_set))
