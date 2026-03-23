from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.access_control.models import OMClientAccess
from apps.access_control.selectors import get_selected_client
from apps.accounts.models import RoleChoices
from apps.audit_logs.models import AuditAction, AuditLog
from apps.core.permissions import IsAdminOrReadOnly
from apps.devices.models import Device, Topic, TopicData
from apps.devices.serializers import DeviceSerializer, TopicDataSerializer, TopicSerializer


def get_accessible_devices(user, client_id=None, require_selection=False):
    queryset = Device.objects.select_related("client").all()
    if user.role == RoleChoices.ADMIN:
        return queryset
    if user.role == RoleChoices.OM:
        client_ids = OMClientAccess.objects.filter(om_user=user).values_list("client_id", flat=True)
        return queryset.filter(client_id__in=client_ids)
    if user.role == RoleChoices.CLIENT:
        client = get_selected_client(user, client_id=client_id, require_selection=require_selection)
        if client:
            return queryset.filter(client_id=client.id)
        return queryset.none()
    return queryset.none()


def get_accessible_topics(user, client_id=None, require_selection=False):
    return Topic.objects.filter(device__in=get_accessible_devices(user, client_id, require_selection)).select_related(
        "device",
        "device__client",
    )


def get_accessible_topic_data(user, client_id=None, require_selection=False):
    return TopicData.objects.filter(topic__in=get_accessible_topics(user, client_id, require_selection)).select_related(
        "topic",
        "topic__device",
    )

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = get_accessible_devices(
            self.request.user,
            client_id=self.request.query_params.get("client_id"),
            require_selection=self.request.user.role == RoleChoices.CLIENT,
        )
        client_id = self.request.query_params.get("client_id")
        device_type = self.request.query_params.get("device_type")
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        if device_type:
            queryset = queryset.filter(device_type=device_type)
        return queryset.order_by("name")

    def perform_create(self, serializer):
        device = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            action=AuditAction.CREATE,
            target_type="Device",
            target_id=str(device.id),
            description=f"Created device {device.serial_number}",
        )

    def perform_update(self, serializer):
        device = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            action=AuditAction.UPDATE,
            target_type="Device",
            target_id=str(device.id),
            description=f"Updated device {device.serial_number}",
        )

    def perform_destroy(self, instance):
        AuditLog.objects.create(
            actor=self.request.user,
            action=AuditAction.DELETE,
            target_type="Device",
            target_id=str(instance.id),
            description=f"Deleted device {instance.serial_number}",
        )
        instance.delete()

    @action(detail=True, methods=["get"], url_path="topics")
    def topics(self, request, pk=None):
        device = get_object_or_404(self.get_queryset(), pk=pk)
        queryset = device.topics.filter(is_active=True).order_by("name")
        serializer = TopicSerializer(queryset, many=True)
        return Response(serializer.data)


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = get_accessible_topics(
            self.request.user,
            client_id=self.request.query_params.get("client_id"),
            require_selection=self.request.user.role == RoleChoices.CLIENT,
        ).filter(is_active=True)
        device_id = self.request.query_params.get("device_id")
        client_id = self.request.query_params.get("client_id")
        if device_id:
            queryset = queryset.filter(device_id=device_id)
        if client_id:
            queryset = queryset.filter(device__client_id=client_id)
        return queryset.order_by("name")

    def perform_create(self, serializer):
        topic = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            action=AuditAction.CREATE,
            target_type="Topic",
            target_id=str(topic.id),
            description=f"Created topic {topic.code}",
        )

    def perform_update(self, serializer):
        topic = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            action=AuditAction.UPDATE,
            target_type="Topic",
            target_id=str(topic.id),
            description=f"Updated topic {topic.code}",
        )

    def perform_destroy(self, instance):
        AuditLog.objects.create(
            actor=self.request.user,
            action=AuditAction.DELETE,
            target_type="Topic",
            target_id=str(instance.id),
            description=f"Deleted topic {instance.code}",
        )
        instance.delete()

    @action(detail=True, methods=["get"], url_path="data")
    def data(self, request, pk=None):
        topic = get_object_or_404(self.get_queryset(), pk=pk)
        queryset = topic.data_points.all()
        recorded_from = request.query_params.get("from")
        recorded_to = request.query_params.get("to")
        limit = request.query_params.get("limit")
        if recorded_from:
            queryset = queryset.filter(recorded_at__gte=recorded_from)
        if recorded_to:
            queryset = queryset.filter(recorded_at__lte=recorded_to)
        if limit:
            queryset = queryset[: int(limit)]
        serializer = TopicDataSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="data/latest")
    def latest_data(self, request, pk=None):
        topic = get_object_or_404(self.get_queryset(), pk=pk)
        data = topic.data_points.order_by("-recorded_at").first()
        serializer = TopicDataSerializer(data)
        return Response(serializer.data if data else None)


class TopicDataViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = TopicData.objects.all()
    serializer_class = TopicDataSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = get_accessible_topic_data(
            self.request.user,
            client_id=self.request.query_params.get("client_id"),
            require_selection=self.request.user.role == RoleChoices.CLIENT,
        )
        topic_id = self.request.query_params.get("topic_id")
        topic_code = self.request.query_params.get("topic_code")
        device_id = self.request.query_params.get("device_id")
        if topic_id:
            queryset = queryset.filter(topic_id=topic_id)
        if topic_code:
            queryset = queryset.filter(topic__code=topic_code)
        if device_id:
            queryset = queryset.filter(topic__device_id=device_id)
        return queryset.order_by("-recorded_at")
