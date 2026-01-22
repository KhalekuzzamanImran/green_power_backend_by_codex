from django.urls import path

from .api.views import (
    RoleListView,
    TokenObtainView,
    TokenLogoutView,
    TokenRefreshView,
    UserListView,
)

urlpatterns = [
    path("roles/", RoleListView.as_view(), name="roles"),
    path("users/", UserListView.as_view(), name="users"),
    path("token/", TokenObtainView.as_view(), name="token-obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/logout/", TokenLogoutView.as_view(), name="token-logout"),
]
