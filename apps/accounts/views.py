from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.models import User
from apps.accounts.serializers import MeSerializer, UserCreateSerializer, UserSerializer
from apps.audit_logs.mixins import AuditModelViewSetMixin
from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import get_action_label, write_audit_log
from apps.core.permissions import CanManageUsers


class UserViewSet(AuditModelViewSetMixin, viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("username")
    permission_classes = [CanManageUsers]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        role = self.request.query_params.get("role")
        if role:
            queryset = queryset.filter(role=role)
        return queryset

    def get_audit_description(self, action, instance):
        return f"{get_action_label(action)} user {instance.username}"


class AuditTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        request = self.context.get("request")
        write_audit_log(
            actor=self.user,
            action=AuditAction.LOGIN,
            target_type="User",
            target_id=self.user.pk,
            description=f"User {self.user.username} logged in via API",
            metadata={
                "source": "api",
                "path": request.path if request else "",
                "method": request.method if request else "",
            },
        )
        return data


@extend_schema(
    tags=["Auth"],
    summary="Get current user bootstrap payload",
    responses={200: MeSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    serializer = MeSerializer(request.user)
    return Response(serializer.data)


class DocumentedTokenObtainPairView(TokenObtainPairView):
    serializer_class = AuditTokenObtainPairSerializer

    @extend_schema(
        tags=["Auth"],
        summary="Login and obtain JWT tokens",
        responses={
            200: OpenApiResponse(
                description="JWT token pair",
                examples=[
                    OpenApiExample(
                        "Token pair",
                        value={
                            "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refresh",
                            "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.access",
                        },
                    )
                ],
            )
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class DocumentedTokenRefreshView(TokenRefreshView):
    @extend_schema(tags=["Auth"], summary="Refresh JWT access token")
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


auth_token_obtain_pair = DocumentedTokenObtainPairView.as_view()
auth_token_refresh = DocumentedTokenRefreshView.as_view()
