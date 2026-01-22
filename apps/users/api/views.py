from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.api.serializers import (
    RoleSerializer,
    TokenObtainSerializer,
    TokenPairSerializer,
    TokenRefreshSerializer,
    TokenLogoutSerializer,
    UserListSerializer,
)
from apps.users.models import Role, User
from apps.users.services.auth_service import (
    authenticate_user,
    blacklist_refresh_token,
    issue_tokens_for_user,
    refresh_tokens,
)
from common.api.time_range import TIME_RANGE_PARAMETERS, TimeRangeFilterMixin
from common.redis_client import get_async_redis


class UserHealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(responses={200: dict})
    def get(self, request, *args, **kwargs):
        return Response({"status": "ok"})


class AsyncRedisHealthView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(responses={200: dict})
    async def get(self, request, *args, **kwargs):
        pong = await get_async_redis().ping()
        return Response({"redis": bool(pong)})


class TokenObtainView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    @extend_schema(request=TokenObtainSerializer, responses={200: TokenPairSerializer})
    def post(self, request, *args, **kwargs):
        serializer = TokenObtainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate_user(**serializer.validated_data)
        if not user:
            raise ValidationError({"detail": "invalid credentials"})
        return Response(issue_tokens_for_user(user))


class TokenRefreshView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(request=TokenRefreshSerializer, responses={200: TokenPairSerializer})
    def post(self, request, *args, **kwargs):
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(refresh_tokens(serializer.validated_data["refresh"]))


class TokenLogoutView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(request=TokenLogoutSerializer, responses={204: None})
    def post(self, request, *args, **kwargs):
        serializer = TokenLogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        blacklist_refresh_token(serializer.validated_data["refresh"])
        return Response(status=204)


@extend_schema(parameters=TIME_RANGE_PARAMETERS, responses={200: RoleSerializer})
class RoleListView(TimeRangeFilterMixin, ListAPIView):
    queryset = Role.objects.all().order_by("-created_at")
    serializer_class = RoleSerializer


@extend_schema(parameters=TIME_RANGE_PARAMETERS, responses={200: UserListSerializer})
class UserListView(TimeRangeFilterMixin, ListAPIView):
    queryset = User.objects.all().order_by("-created_at")
    serializer_class = UserListSerializer
