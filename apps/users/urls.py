from django.urls import path

from .api.views import (
    TokenObtainView,
    TokenLogoutView,
    TokenRefreshView,
)

urlpatterns = [
    path("token/", TokenObtainView.as_view(), name="token-obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/logout/", TokenLogoutView.as_view(), name="token-logout"),
]
