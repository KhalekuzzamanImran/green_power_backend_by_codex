from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from apps.core.admin_site import hardened_admin_site

urlpatterns = [
    path("panel/", include("apps.panel.urls")),
    path('admin/', hardened_admin_site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/v1/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.clients.urls")),
    path("api/v1/", include("apps.devices.urls")),
    path("api/v1/", include("apps.dashboards.urls")),
    path("api/v1/", include("apps.access_control.urls")),
    path("api/v1/", include("apps.thresholds.urls")),
    path("api/v1/", include("apps.audit_logs.urls")),
]
