from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.api.serializers import (
    TokenObtainSerializer,
    TokenPairSerializer,
    TokenRefreshSerializer,
    TokenLogoutSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)
from apps.users.services.auth_service import (
    authenticate_user,
    blacklist_refresh_token,
    issue_tokens_for_user,
    refresh_tokens,
)
from apps.users.services.user_service import register_user
from common.exceptions import UserAlreadyExistsError
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


class UserRegistrationView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(request=UserRegistrationSerializer, responses={201: UserSerializer})
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = register_user(**serializer.validated_data)
        except UserAlreadyExistsError as exc:
            raise ValidationError({"detail": str(exc)}) from exc
        except DjangoValidationError as exc:
            raise ValidationError({"password": exc.messages}) from exc
        return Response(UserSerializer(user).data, status=201)


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
