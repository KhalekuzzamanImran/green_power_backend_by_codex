from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from common.health import HealthCheckView, ReadinessCheckView

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="index"),
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/health/", HealthCheckView.as_view(), name="health"),
    path("api/ready/", ReadinessCheckView.as_view(), name="ready"),
    path("api/users/", include("apps.users.urls")),
]
