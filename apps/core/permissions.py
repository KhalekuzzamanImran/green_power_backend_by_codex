from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "ADMIN"


class IsOMRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "OM"


class IsClientRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "CLIENT"


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role == "ADMIN"


class CanManageUsers(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "ADMIN"


class CanSetThreshold(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in {"ADMIN", "OM"}
