from rest_framework.routers import DefaultRouter
from django.urls import path

from apps.accounts.views import UserViewSet, auth_token_obtain_pair, auth_token_refresh, me_view

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path("auth/login/", auth_token_obtain_pair, name="token_obtain_pair"),
    path("auth/refresh/", auth_token_refresh, name="token_refresh"),
    path("auth/me/", me_view, name="auth_me"),
]

urlpatterns += router.urls
