from django.urls import path

from apps.panel.views.access import (
    OMClientAccessCreateView,
    OMClientAccessDeleteView,
    OMClientAccessListView,
    OMClientAccessUpdateView,
    UserClientAccessCreateView,
    UserClientAccessDeleteView,
    UserClientAccessListView,
    UserClientAccessUpdateView,
)
from apps.panel.views.audit_logs import AuditLogListView
from apps.panel.views.auth import PanelLoginView, PanelLogoutView
from apps.panel.views.clients import (
    ClientCodeSuggestionView,
    ClientCodeValidationView,
    ClientCreateView,
    ClientDeleteView,
    ClientDetailView,
    ClientListView,
    ClientScopeOptionsView,
    ClientTypeCreateView,
    ClientTypeDeleteView,
    ClientTypeListView,
    ClientTypeUpdateView,
    ClientUpdateView,
)
from apps.panel.views.device_data import DeviceDataCreateView, DeviceDataDeleteView, DeviceDataListView, DeviceDataUpdateView
from apps.panel.views.device_states import (
    DeviceStateCreateView,
    DeviceStateDeleteView,
    DeviceStateDetailView,
    DeviceStateListView,
    DeviceStateUpdateView,
)
from apps.panel.views.devices import DeviceCreateView, DeviceDeleteView, DeviceDetailView, DeviceListView, DeviceUpdateView
from apps.panel.views.home import PanelHomeView
from apps.panel.views.thresholds import ThresholdCreateView, ThresholdDeleteView, ThresholdListView, ThresholdUpdateView
from apps.panel.views.users import UserCreateView, UserDeleteView, UserListView, UserUpdateView

app_name = "panel"

urlpatterns = [
    path("login/", PanelLoginView.as_view(), name="login"),
    path("logout/", PanelLogoutView.as_view(), name="logout"),
    path("", PanelHomeView.as_view(), name="home"),
    path("clients/scope-options/", ClientScopeOptionsView.as_view(), name="client-scope-options"),
    path("clients/code-suggestion/", ClientCodeSuggestionView.as_view(), name="client-code-suggestion"),
    path("clients/code-validation/", ClientCodeValidationView.as_view(), name="client-code-validation"),
    path("client-types/", ClientTypeListView.as_view(), name="client-types"),
    path("client-types/add/", ClientTypeCreateView.as_view(), name="client-type-add"),
    path("client-types/<uuid:pk>/edit/", ClientTypeUpdateView.as_view(), name="client-type-edit"),
    path("client-types/<uuid:pk>/delete/", ClientTypeDeleteView.as_view(), name="client-type-delete"),
    path("clients/", ClientListView.as_view(), name="clients"),
    path("clients/add/", ClientCreateView.as_view(), name="client-add"),
    path("clients/<uuid:client_id>/", ClientDetailView.as_view(), name="client-detail"),
    path("clients/<uuid:pk>/edit/", ClientUpdateView.as_view(), name="client-edit"),
    path("clients/<uuid:pk>/delete/", ClientDeleteView.as_view(), name="client-delete"),
    path("devices/", DeviceListView.as_view(), name="devices"),
    path("devices/add/", DeviceCreateView.as_view(), name="device-add"),
    path("devices/<uuid:device_id>/", DeviceDetailView.as_view(), name="device-detail"),
    path("devices/<uuid:pk>/edit/", DeviceUpdateView.as_view(), name="device-edit"),
    path("devices/<uuid:pk>/delete/", DeviceDeleteView.as_view(), name="device-delete"),
    path("device-states/", DeviceStateListView.as_view(), name="device-states"),
    path("device-states/add/", DeviceStateCreateView.as_view(), name="device-state-add"),
    path("device-states/<uuid:state_id>/", DeviceStateDetailView.as_view(), name="device-state-detail"),
    path("device-states/<uuid:pk>/edit/", DeviceStateUpdateView.as_view(), name="device-state-edit"),
    path("device-states/<uuid:pk>/delete/", DeviceStateDeleteView.as_view(), name="device-state-delete"),
    path("device-data/", DeviceDataListView.as_view(), name="device-data"),
    path("device-data/add/", DeviceDataCreateView.as_view(), name="device-data-add"),
    path("device-data/<uuid:pk>/edit/", DeviceDataUpdateView.as_view(), name="device-data-edit"),
    path("device-data/<uuid:pk>/delete/", DeviceDataDeleteView.as_view(), name="device-data-delete"),
    path("users/", UserListView.as_view(), name="users"),
    path("users/add/", UserCreateView.as_view(), name="user-add"),
    path("users/<uuid:pk>/edit/", UserUpdateView.as_view(), name="user-edit"),
    path("users/<uuid:pk>/delete/", UserDeleteView.as_view(), name="user-delete"),
    path("access/user-client/", UserClientAccessListView.as_view(), name="user-client-access"),
    path("access/user-client/add/", UserClientAccessCreateView.as_view(), name="user-client-access-add"),
    path("access/user-client/<uuid:pk>/edit/", UserClientAccessUpdateView.as_view(), name="user-client-access-edit"),
    path("access/user-client/<uuid:pk>/delete/", UserClientAccessDeleteView.as_view(), name="user-client-access-delete"),
    path("access/om-client/", OMClientAccessListView.as_view(), name="om-client-access"),
    path("access/om-client/add/", OMClientAccessCreateView.as_view(), name="om-client-access-add"),
    path("access/om-client/<uuid:pk>/edit/", OMClientAccessUpdateView.as_view(), name="om-client-access-edit"),
    path("access/om-client/<uuid:pk>/delete/", OMClientAccessDeleteView.as_view(), name="om-client-access-delete"),
    path("thresholds/", ThresholdListView.as_view(), name="thresholds"),
    path("thresholds/add/", ThresholdCreateView.as_view(), name="threshold-add"),
    path("thresholds/<uuid:pk>/edit/", ThresholdUpdateView.as_view(), name="threshold-edit"),
    path("thresholds/<uuid:pk>/delete/", ThresholdDeleteView.as_view(), name="threshold-delete"),
    path("audit-logs/", AuditLogListView.as_view(), name="audit-logs"),
]
